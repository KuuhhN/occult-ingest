<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="screenshots/hero-dark.svg">
    <img src="screenshots/hero-light.svg" alt="贤者之石" width="600">
  </picture>
</p>

<p align="center">
  <strong>贤者之石 — 神秘学知识库 · 自带 27 本书的笔记 + 可扩展工具链</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-≥3.10-blue?logo=python" alt="Python"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
  <a href="https://github.com/KuuhhN/occult-ingest/stargazers"><img src="https://img.shields.io/github/stars/KuuhhN/occult-ingest?style=social" alt="Stars"></a>
</p>

---

## 💎 这是什么

**贤者之石** 是一套神秘学知识管理方案，包含两样东西：

| | 工具链 | 知识库 |
|---|---|---|
| 内容 | `ocr_extract.py` + `format_ocr.py` | ~150 篇已审核笔记 |
| 作用 | 让你处理自己的 PDF | 让你立刻开始阅读和探索 |
| 可选？ | 核心 | 可替换 |

你下载后，先用自带的知识库了解神秘学体系的全貌，再用工具链把自己的书加进来。

---

## 🚀 三步开始

### 1. 下载

```bash
git clone https://github.com/KuuhhN/occult-ingest.git
```

### 2. 用 Obsidian 打开知识库

1. 下载安装 [Obsidian](https://obsidian.md)（免费）
2. 打开 Obsidian → 点击 "Open folder as vault"
3. 选择 `occult-ingest/knowledge-base/` 文件夹
4. 点 "Trust author and enable plugins"

成功后你会看到：

```
knowledge-base/
├── 00-MOC/             ← 从这里开始！神秘学总览
├── 01-知识库/           ← 按炼金术/塔罗/卡巴拉/…分类
├── 02-文献库/           ← PDF + OCR 原文（27本）
├── 03-导读/            ← 每本书的速读指南
├── 05-摘要/            ← 按章节分层的详细摘要
├── 06-笔记/            ← 精读笔记（信息密度~50%）
└── 99-模板/            ← 笔记模板
```

> 📸 *按 Ctrl+E 切换到阅读模式；按 Ctrl+单击笔记中的页码链接直接跳转到 PDF 对应页面。*

### 3. 安装工具链（当你需要处理新书时）

```bash
pip install pdfplumber tencentcloud-sdk-python-ocr pymupdf pangu
export TENCENT_SECRET_ID="你的腾讯云 SecretId"
export TENCENT_SECRET_KEY="你的腾讯云 SecretKey"
```

然后把 PDF 变成笔记：

```bash
# OCR 提取
python occult-ingest/ocr_extract.py "新书.pdf" "书名" "作者"

# 精排版格式化
python occult-ingest/format_ocr.py "原文.md" "精排版.md" \
    --title "《书名》" --meta "作者 | 出版社"
```

---

## 📊 知识库现状

| 体系 | 已收录 | 状态 |
|------|--------|------|
| 🜁 炼金术 | 7 本 | ✅ 丰富 |
| 🝞 魔法实践 | 14 本 | ✅ 丰富 |
| 🏛️ 希腊宗教 | 1 本 | ✅ |
| ☆ 塔罗与卡巴拉 | 1 本 | ✅ |
| 🗲 占星学 | 1 本 | ✅ |
| 🜃 赫尔墨斯主义 | 1 本 | ✅ |
| ☽ 灵修与冥想 | 1 本 | ✅ |
| 🐱 现代巫术 | 2 本 | ✅ 新增 |
| 卡巴拉 | 0 | ⏳ 待填充 |
| 威卡 | 0 | ⏳ |
| 神话学 | 0 | ⏳ |
| 符号学 | 0 | ⏳ |

> 持续更新中。contributions welcome。

---

## 🔄 完整流水线

```
PDF 扫描件
  │
  ▼
ocr_extract.py  →  OCR 原文（腾讯云，逐页识别）
  │
  ▼
format_ocr.py  →  精排版（去出版信息、去页眉、合并断句、中英间距规范化）
  │
  ▼
AI 辅助精读   →  三份笔记：
  ├── 📖 导读（3分钟速览）
  ├── 📋 摘要目录（按章节分层）
  └── 📝 精读笔记（~50% 密度 + 页码溯源）
  │
  ▼
MOC 关联     →  自动纳入对应知识体系，跨书连线
```

---

## 📂 仓库结构

```
occult-ingest/
├── occult-ingest/         ← 工具脚本
│   ├── SKILL.md           ← 完整工作流说明书
│   ├── ocr_extract.py     ← 腾讯云 OCR 引擎
│   ├── format_ocr.py      ← 精排版引擎 v0.3
│   └── examples/          ← 单篇示例
├── knowledge-base/        ← 完整知识库（Obsidian Vault）
│   ├── 00-MOC/            ← 总览索引
│   ├── 01-知识库/         ← 按体系分类的条目
│   ├── 02-文献库/          ← 完整 PDF 原典（27 本）
│   ├── 03-导读/           ← 快速导读
│   ├── 05-摘要/           ← 分层摘要目录
│   ├── 06-笔记/           ← 精读笔记
│   └── 99-模板/           ← 笔记模板
├── screenshots/           ← 占位截图
├── README.md
├── CHANGELOG.md
└── requirements.txt
```

> ⚠️ 不要直接往 `02-文献库/` 放 PDF。使用 `git clone` 下载本仓库即可获得完整知识库（含 27 本 PDF + ~150 篇笔记）。

---

## 🛠️ 命令行参考

| 工具 | 必需参数 | 可选参数 |
|------|---------|---------|
| `ocr_extract.py` | pdf_path, title | author, --vault, OCCULT_VAULT_PATH |
| `format_ocr.py` | raw_path, out_path | --title, --meta, --headers, --raw-page-link |

---

## 📋 更新日志

[CHANGELOG.md](./CHANGELOG.md)

---

## ⚠️ 免责声明

[详见 DISCLAIMER.md](./DISCLAIMER.md)。简而言之：本仓库资料仅供个人学习研究，笔记为原创整理，PDF 来源于网络公开资源。如有版权问题请联系我处理。

---

## 📜 许可

MIT License — 工具和笔记均可自由使用、修改、分发。
