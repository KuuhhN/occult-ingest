# 更新日志

本文件记录 `occult-ingest` 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 新增
- 中文名「贤者之石」正式启用
- 知识库扩展到 15 本书、11 个知识体系

### 计划中
- 跨书知识图谱自动连线
- 更多导出格式支持（Notion、Logseq）

---

## [0.1.0] — 2026-06-26

### 新增
- `ocr_extract.py` — 腾讯云 OCR 引擎，PDF → 带页码标记的 Markdown 原文
- `format_ocr.py` — 精排版引擎 v0.3，去出版元数据 / 去页眉 / 合并跨页断句 / 中英文间距规范化
- `SKILL.md` — 完整 8 步工作流说明书（OCR → 精排版 → AI 精读 → PDF 归档 → 知识条目 → 日志）
- 知识库目录结构设计（00-MOC / 01-知识库 / 02-文献库 / 03-导读 / 04-日志 / 05-摘要 / 06-笔记）
- MIT 开源协议
- GitHub Actions 就绪的 `requirements.txt`

### 变更
- 将原有两个独立 Skill（`occult-ingest` + `ocr-polish`）合并为一个统一的流水线

---

## [0.1.1] — 2026-06-27

### 新增
- 质量检验规则：笔记必须包含原文中的具体引述或案例作为证据
- 日志格式明确化：每日日志统一为 `YYYY-MM-DD.md`

### 变更
- OCR 引擎从 `GeneralBasicOCR` 升级为 `GeneralFastOCR`（速度优化）

---

## [0.1.2] — 2026-06-28

### 变更
- `SKILL.md` 工作流描述精简
- `ocr_extract.py` 优化错误处理和重试逻辑

---

## 版本号说明

| 版本段 | 含义 |
|--------|------|
| 主版本号 | 不兼容的 API 修改 / 大架构变更 |
| 次版本号 | 向下兼容的功能新增 |
| 修订号 | 向下兼容的问题修正 |

当前版本：**0.1.2** — 早期预览阶段，API 可能变动。
