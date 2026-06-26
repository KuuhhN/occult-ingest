"""
OCR 原文 → 精排版 格式化引擎 v0.3（通用版）
核心思路：书的内容是连续流淌的，不应被 PDF 物理页边界切割。
  - 去除所有出版元数据（CIP、版权页、ISBN）
  - 去除印刷书页眉（每页重复的章节标题）
  - 按章节/段落自然边界重组全文
  - 保留：大标题、目录、前言、正文等

用法：
    python format_ocr.py <原文.md> <精排版.md> [--title <书名>] [--meta <元数据>] [--headers <页眉列表>]

示例：
    python format_ocr.py 炼金术_原文.md 炼金术_精排版.md \\
        --title "《炼金术》" \\
        --meta "徐德伟 编著 | 哈尔滨出版社 | 2006年8月第1版" \\
        --headers "第一章 历史与传说之间,第二章 踏上天堂之路,第三章 神圣的艺术,第四章 见证永生之奥秘,CONTENTS,目录"
"""
import re
import pangu
import argparse

def is_meta_block(block: str) -> bool:
    """判断是否为元数据块（版权页、CIP、ISBN 等）"""
    for pat in META_PATTERNS:
        if re.search(pat, block):
            return True
    return False

def is_header_line(line: str, running_headers: list[str] | None = None) -> bool:
    """判断是否为印刷页眉"""
    headers = running_headers if running_headers is not None else []
    stripped = line.strip().replace(' ', '').replace('，', '').replace(',', '')
    for h in headers:
        h_clean = h.replace(' ', '').replace('，', '').replace(',', '')
        if stripped == h_clean or h_clean in stripped:
            return True
    return False

def format_ocr_to_polished(raw_text: str, title: str = "", meta: str = "",
                            running_headers: list[str] | None = None,
                            raw_page_link: str = "") -> str:
    
    # ===== 阶段 1：剥离所有页面边界，熔为一炉 =====
    text = re.sub(r'## 第\d+页\n+', '\n', raw_text)
    text = re.sub(r'# .*?OCR 原文.*?\n\n', '', text)
    text = re.sub(r'> .*?\n\n', '', text)
    text = re.sub(r'\n\d{3}\n', '\n', text)  # 孤立页码
    text = re.sub(r'-\n', '', text)           # 断字连字符
    text = re.sub(r'\n[A-Za-z]\n', '\n', text)  # 单字母孤行
    
    # ===== 阶段 2：逐块清理——去元数据、去页眉、合碎片 =====
    raw_blocks = text.split('\n\n')
    content_blocks = []
    
    for block in raw_blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        
        # 去元数据
        full = ''.join(lines)
        if is_meta_block(full):
            continue
        
        # 去页眉行
        clean_lines = [l for l in lines if not is_header_line(l, running_headers)]
        if not clean_lines:
            continue
        
        # 拼接为连续文本
        merged = ''.join(clean_lines)
        if len(merged) < 3:
            continue
        content_blocks.append(merged)
    
    # ===== 阶段 3：智能段落重组 =====
    # 现在所有内容是一串连续块，需要识别真正的段落边界
    sentence_end = '。！？）\"\'.!?;:'
    paragraphs = []
    i = 0
    
    while i < len(content_blocks):
        cur = content_blocks[i]
        
        # 章节标题独立
        if re.match(r'^(第[一二三四五六七八九十百]+章|前言|FOREWORD|目录|CONTENTS)', cur):
            paragraphs.append(cur)
            i += 1
            continue
        
        # 二级标题独立
        if re.match(r'^\d+[\.\、]\s*.{3,40}$', cur):
            paragraphs.append(cur)
            i += 1
            continue
        
        # 尝试与下一块合并（跨页续句）
        if i + 1 < len(content_blocks):
            nxt = content_blocks[i + 1]
            # 下一块是标题就不合
            if re.match(r'^(第[一二三四五六七八九十百]+章|前言|FOREWORD|目录|CONTENTS|\d+[\.\、])', nxt):
                paragraphs.append(cur)
                i += 1
                continue
            
            should_merge = False
            # 当前块结尾不是句末标点
            if cur and cur[-1] not in sentence_end and len(cur) > 5:
                should_merge = True
            # 当前块以「的」「了」等结尾
            if cur and len(cur) > 5 and cur[-1] in '的了着在和到与及或为从':
                should_merge = True
            # 下一块首字符是标点
            if nxt and nxt[0] in '，。、；：！？）)]':
                should_merge = True
            
            if should_merge:
                paragraphs.append(cur + nxt)
                i += 2
                continue
        
        paragraphs.append(cur)
        i += 1
    
    # ===== 阶段 4：标题 Markdown 化 =====
    formatted = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        
        # 主章标题
        m = re.match(r'^(第[一二三四五六七八九十百]+章)(.{1,40})$', p)
        if m:
            subtitle = m.group(2).strip()
            formatted.append(f'# {m.group(1)} {subtitle}')
            continue
        
        # 二级小节
        if re.match(r'^\d+[\.\、]\s*.{3,50}$', p):
            formatted.append(f'## {p}')
            continue
        
        # 目录
        if p in ('目录', 'CONTENTS'):
            formatted.append('## 目录')
            continue
        
        # 前言
        if p in ('前言', 'FOREWORD'):
            formatted.append('## 前言')
            continue
        
        formatted.append(p)
    
    # ===== 阶段 5：pangu 中英间距 + 收尾 =====
    result = '\n\n'.join(formatted)
    result = pangu.spacing(result)
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r'^(#{1,6})\s+', r'\1 ', result, flags=re.MULTILINE)
    
    # ===== 组装最终输出 =====
    output = f'# {title}\n\n' if title else ''
    if meta:
        output += f'> {meta}\n\n'
    if raw_page_link:
        output += f'> 🔒 原文存档：[[{raw_page_link}]] | 精排版从此派生\n\n'
    output += result
    
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OCR 原文 → 精排版 格式化引擎')
    parser.add_argument('raw_path', help='原文文件路径（OCR 输出）')
    parser.add_argument('out_path', help='精排版输出路径')
    parser.add_argument('--title', default='', help='书名，如 "《炼金术》"')
    parser.add_argument('--meta', default='', help='元数据，如 "徐德伟 编著 | 哈尔滨出版社"')
    parser.add_argument('--headers', default='', help='印刷页眉列表，用逗号分隔')
    parser.add_argument('--raw-page-link', default='', help='原文 Obsidian 链接名称用于脚注')
    args = parser.parse_args()

    running_headers = [h.strip() for h in args.headers.split(',')] if args.headers else []

    with open(args.raw_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    polished = format_ocr_to_polished(
        raw,
        title=args.title,
        meta=args.meta,
        running_headers=running_headers,
        raw_page_link=args.raw_page_link
    )

    with open(args.out_path, 'w', encoding='utf-8') as f:
        f.write(polished)

    print(f'v0.3 formatted: {args.raw_path} → {args.out_path}')
