# Occult Ingest — 神秘学 PDF 资料入库工具

> OCR 提取 + 精排版格式化 + AI 笔记生成，一站式神秘学 PDF 资料管理流水线。

## 🌟 功能

| 步骤 | 工具 | 说明 |
|------|------|------|
| 1 | `ocr_extract.py` | 调用腾讯云 OCR，将 PDF 逐页识别为带页码标记的原文 Markdown |
| 2 | `format_ocr.py` | 将原文格式化为精排版：去版权页/CIP/ISBN、去印刷页眉、智能合并跨页断句、标题 Markdown 化、中英文间距规范化 |
| 3 | AI 精读 | 生成导读、摘要目录、精读笔记三份结构化笔记（需配合 LLM 使用） |
| 4 | PDF 归档 | 将 PDF 复制到知识库，建立 Obsidian 双向链接 |

## 🚀 快速开始

### 依赖安装

```bash
pip install pdfplumber tencentcloud-sdk-python-ocr pymupdf pangu
```

### 配置腾讯云 OCR

注册 [腾讯云 OCR](https://console.cloud.tencent.com/ocr) 获取 SecretId 和 SecretKey，通过环境变量传入：

```bash
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"
```

### 使用

```bash
# 第1步：OCR 提取原文
python occult-ingest/ocr_extract.py "path/to/book.pdf" "书名" "作者"

# 第2步：格式化为精排版
python occult-ingest/format_ocr.py \
    "02-文献库/经典文献/书名_原文.md" \
    "02-文献库/经典文献/书名_精排版.md" \
    --title "《书名》" \
    --meta "作者 编著 | 出版社" \
    --headers "第一章 xxx,第二章 xxx,第三章 xxx,第四章 xxx" \
    --raw-page-link "书名_原文"
```

完整流程参考 `occult-ingest/SKILL.md`（Reasonix 技能说明书）。

## 📂 推荐的知识库目录结构（Obsidian Vault）

```
00-MOC/      总览索引
01-知识库/   知识条目（按体系分子目录）
02-文献库/   原文 PDF + OCR 原文 + 精排版
03-导读/     快速入门导读
04-日志/     每日学习记录
05-摘要/     分层摘要目录
06-笔记/     精读笔记（~50% 密度）
99-模板/     笔记模板
```

## 🔧 参数说明

### ocr_extract.py

| 参数 | 说明 |
|------|------|
| `pdf_path` | PDF 文件路径（必需） |
| `title` | 书名（可选，默认"未命名"） |
| `author` | 作者（可选） |
| `--vault` | 知识库根目录（可选，默认自动探测） |
| `OCCULT_VAULT_PATH` | 同上，环境变量方式 |

### format_ocr.py

| 参数 | 说明 |
|------|------|
| `raw_path` | 原文文件路径（OCR 输出） |
| `out_path` | 精排版输出路径 |
| `--title` | 书名 |
| `--meta` | 元数据字符串 |
| `--headers` | 印刷页眉列表（逗号分隔） |
| `--raw-page-link` | 原文 Obsidian 内部链接名 |

## 📜 开源协议

MIT License — 详见 [LICENSE](./LICENSE)。

## 🙏 致谢

- [腾讯云 OCR](https://cloud.tencent.com/product/ocr)
- [pangu](https://github.com/vinta/pangu) — 中英文间距规范化
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [pymupdf](https://pymupdf.readthedocs.io/)
