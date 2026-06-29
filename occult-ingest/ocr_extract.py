"""
OCR 提取脚本 — 调用腾讯云 OCR 将 PDF 转为带页码标记的原文。

用法：
    python ocr_extract.py <pdf路径> <书名> [作者] [--vault <vault根目录>]

环境变量：
    TENCENT_SECRET_ID     腾讯云 SecretId（必需）
    TENCENT_SECRET_KEY    腾讯云 SecretKey（必需）
    OCCULT_VAULT_PATH     知识库根目录（可选，默认 ../occult-vault）

输出：<vault>/02-文献库/经典文献/<书名>_原文.md

⚠️ 隐私提示：PDF 内容将以图片形式发送到腾讯云 OCR 服务器进行识别。
   请确保不涉及个人隐私或受版权严格保护的材料。
"""
import sys, os, base64, json, time, argparse, re, tempfile
import pdfplumber
from tencentcloud.common import credential
from tencentcloud.ocr.v20181119 import ocr_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

def sanitize_filename(name: str) -> str:
    """去除文件名非法字符，防止路径穿越"""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)

def get_vault_path(cli_vault: str | None = None) -> str:
    """确定知识库根目录：CLI 参数 > 环境变量 > 默认值"""
    if cli_vault:
        return cli_vault
    env = os.environ.get('OCCULT_VAULT_PATH')
    if env:
        return env
    # 默认定位到项目同级目录下的 occult-vault
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, '..', '..', '..', 'occult-vault'))

def ocr_pdf(pdf_path: str, title: str, author: str = "", vault_path: str | None = None):
    secret_id = os.environ.get('TENCENT_SECRET_ID')
    secret_key = os.environ.get('TENCENT_SECRET_KEY')
    if not secret_id or not secret_key:
        raise RuntimeError("请设置 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY 环境变量")

    vault = get_vault_path(vault_path)
    cred_obj = credential.Credential(secret_id, secret_key)
    client = ocr_client.OcrClient(cred_obj, 'ap-guangzhou')
    pdf = pdfplumber.open(pdf_path)
    total = len(pdf.pages)

    # 四种免费配额，按优先级排列：Fast → Basic → Accurate → Handwriting
    api_chain = [
        ('GeneralFastOCR',      models.GeneralFastOCRRequest,      0),
        ('GeneralBasicOCR',     models.GeneralBasicOCRRequest,     0),
        ('GeneralAccurateOCR',  models.GeneralAccurateOCRRequest,  0),
    ]
    active_idx = 0  # 当前使用的 API 索引

    all_pages = []
    i = 0
    while i < total:
        try:
            page = pdf.pages[i]
            img_path = os.path.join(tempfile.gettempdir(), f'_ocr_tmp_{i}.png')
            img = page.to_image(resolution=200)
            img.save(img_path, 'PNG')

            with open(img_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode()

            api_name, req_class, call_count = api_chain[active_idx]
            req = req_class()
            req.ImageBase64 = img_base64
            api_method = getattr(client, api_name)
            resp = api_method(req)
            data = json.loads(resp.to_json_string())
            texts = [item['DetectedText'] for item in data.get('TextDetections', [])]
            api_chain[active_idx] = (api_name, req_class, call_count + 1)

            if texts:
                all_pages.append(f'## 第{i+1}页\n\n' + '\n'.join(texts))

            os.remove(img_path)
            time.sleep(0.3)

            if (i+1) % 50 == 0:
                print(f'  OCR 进度: {i+1}/{total} (当前API: {api_name})')
            i += 1

        except TencentCloudSDKException as e:
            if os.path.exists(img_path):
                os.remove(img_path)
            code = str(e.code) if hasattr(e, 'code') else str(e)
            # 配额耗尽 → 自动切换下一个 API
            if 'ResourcePackageRunOut' in code or 'ResourceUnavailable' in code:
                if active_idx < len(api_chain) - 1:
                    old_api = api_chain[active_idx][0]
                    active_idx += 1
                    new_api = api_chain[active_idx][0]
                    print(f'  [切换] {old_api} 配额耗尽 -> 切换到 {new_api} (第{i+1}页)')
                    time.sleep(1)
                    # 不递增 i，重试当前页
                    continue
                else:
                    print(f'  [耗尽] 全部四种 API 配额已用完，在第 {i+1} 页停止')
                    break
            else:
                print(f'  API error p{i+1}: {code}')
                i += 1
                time.sleep(1)
        except Exception as e:
            if os.path.exists(img_path):
                os.remove(img_path)
            print(f'  error p{i+1}: {e}')
            i += 1
            time.sleep(1)

    pdf.close()

    safe_title = sanitize_filename(title)
    meta = f'{author} 编著' if author else ''
    raw = f'# 《{title}》OCR 原文（腾讯云，未经排版）\n\n> {meta}\n\n'
    raw += '\n\n'.join(all_pages)

    out_dir = os.path.join(vault, '02-文献库', '经典文献')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{safe_title}_原文.md')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(raw)

    # 用 ASCII 安全的方式输出统计
    stats = ', '.join(f'{name}: {n}' for name, _, n in api_chain[:active_idx+1])
    print(f'  [OK] 原文已保存: {out_path}')
    print(f'  共 {len(all_pages)}/{total} 页 | API使用: {stats}')
    return out_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='腾讯云 OCR PDF 提取')
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('title', nargs='?', default='未命名', help='书名')
    parser.add_argument('author', nargs='?', default='', help='作者')
    parser.add_argument('--vault', help='知识库根目录（可选）')
    args = parser.parse_args()
    
    print("⚠️  隐私提示：PDF 内容将以图片形式发送到腾讯云 OCR 服务器进行识别。", file=sys.stderr)
    print("   请确保不涉及个人隐私或受版权严格保护的材料。", file=sys.stderr)
    
    ocr_pdf(args.pdf_path, args.title, args.author, args.vault)
