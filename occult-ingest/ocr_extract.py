"""
OCR 提取脚本 — 调用腾讯云 OCR 将 PDF 转为带页码标记的原文。

用法：
    python ocr_extract.py <pdf路径> <书名> [作者] [--vault <vault根目录>]

环境变量：
    TENCENT_SECRET_ID     腾讯云 SecretId（必需）
    TENCENT_SECRET_KEY    腾讯云 SecretKey（必需）
    OCCULT_VAULT_PATH     知识库根目录（可选，默认 ../occult-vault）

输出：<vault>/02-文献库/经典文献/<书名>_原文.md
"""
import sys, os, base64, json, time, argparse
import pdfplumber
from tencentcloud.common import credential
from tencentcloud.ocr.v20181119 import ocr_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

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
    
    all_pages = []
    for i in range(total):
        try:
            page = pdf.pages[i]
            img_path = os.path.join(os.path.dirname(pdf_path) or '.', f'_ocr_tmp_{i}.png')
            img = page.to_image(resolution=200)
            img.save(img_path, 'PNG')
            
            with open(img_path, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode()
            
            req = models.GeneralBasicOCRRequest()
            req.ImageBase64 = img_base64
            req.LanguageType = 'zh'
            resp = client.GeneralBasicOCR(req)
            data = json.loads(resp.to_json_string())
            texts = [item['DetectedText'] for item in data.get('TextDetections', [])]
            
            if texts:
                all_pages.append(f'## 第{i+1}页\n\n' + '\n'.join(texts))
            
            os.remove(img_path)
            time.sleep(0.3)
            
            if (i+1) % 50 == 0:
                print(f'  OCR 进度: {i+1}/{total}')
                
        except TencentCloudSDKException as e:
            print(f'  API 错误 p{i+1}: {e.code}')
            time.sleep(1)
        except Exception as e:
            print(f'  错误 p{i+1}: {e}')
            time.sleep(1)
    
    pdf.close()
    
    meta = f'{author} 编著' if author else ''
    raw = f'# 《{title}》OCR 原文（腾讯云，未经排版）\n\n> {meta}\n\n'
    raw += '\n\n'.join(all_pages)
    
    out_dir = os.path.join(vault, '02-文献库', '经典文献')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'{title}_原文.md')
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(raw)
    
    print(f'  ✅ 原文已保存: {out_path}')
    print(f'  共 {len(all_pages)}/{total} 页')
    return out_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='腾讯云 OCR PDF 提取')
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('title', nargs='?', default='未命名', help='书名')
    parser.add_argument('author', nargs='?', default='', help='作者')
    parser.add_argument('--vault', help='知识库根目录（可选）')
    args = parser.parse_args()
    
    ocr_pdf(args.pdf_path, args.title, args.author, args.vault)
