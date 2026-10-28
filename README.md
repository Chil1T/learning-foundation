# Learning Foundation

> **专为 AI 智能体设计的认知级学习与科研精读套件 (Agent Skills)**  
> 拒绝答案直接灌输与信息泛滥，让 AI 真正带你搞懂概念、啃透论文、沉淀思考。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Specification](https://img.shields.io/badge/Agent_Skills-Open_Standard-green.svg)](https://agentskills.io/specification)
[![Version](https://img.shields.io/badge/Version-0.2.0-orange.svg)](VERSION)

---

## ✨ 为什么需要 Learning Foundation？

普通对话式 AI 在辅助学习时，往往存在四大痛点：

* **“虚假掌握”的错觉**：AI 一下子抛出长篇大论或直接给出答案，剥夺了人的探索与推理过程。你以为看懂了，自己一做题依然卡壳。
* **学术论文“浮于表面”**：读论文往往沦为“论文速读”或“摘要翻译”，遇到复杂的公式推导、模型假设与适用边界，AI 无法带你深入论证。
* **上下文重置，学习断档**：每开一个新会话，AI 就把你的认知背景忘得一干二净，无法记录你到底在哪里卡住、学到了哪一步。
* **生态绑架与隐私担忧**：市面上的知识库方案往往强制绑定专有软件、私有数据库或云端账号，甚至侵入用户的私人笔记目录。

**Learning Foundation** 是一套遵循开放 [Agent Skills 规范](https://agentskills.io/specification) 的纯本地智能体技能套件。它为智能体注入专业的认知辅导与学术推演工作流，**纯净、解耦、本地优先 (Local-First)**，不绑定任何专有笔记软件，开箱即用。

---

## 📦 技能矩阵与组合

Learning Foundation 包含 8 个经过严格解耦的标准技能单元，每个技能均可独立使用：

### 1. 通用认知学习流（[默认推荐组合](presets/default.md)）
* **`learning-entry`**：**学习导航入口**。从“我想学 X”的宽泛想法中收束出一个今天立即可完成的小切口，并设立清晰的断点。
* **`concept-tutor`**：**概念深度辅导**。拒绝枯燥复读教科书定义；用具象对象、逻辑推导与关键反例逐步建立直觉，并核对你的真实理解。
* **`learning-plan-designer`**：**动态路线规划**。从目标、当前基础、前置依赖和现实期限出发，制定可落地、可检查的学习里程碑。
* **`learning-state-reconciler`**：**断点与状态对齐**。跨会话对齐理解状态，记住你真正懂了什么、在哪个公式卡住，随时从中断点继续。

### 2. 学术科研精读流（[科研进阶组合](presets/research.md)）
* **`research-learning-entry`**：**科研入口与主线把控**。紧扣论文主线或导师要求，锁定今天的研读段落，防止精力被细枝末节分散。
* **`paper-deep-reader`**：**论文深度领读**。拆解公式假设、适用边界与论证链条，搞清楚“为什么作者这一步要这么做”。
* **`research-meeting-prep`**：**组会推演与答辩准备**。从真实学习证据中提炼汇报逻辑与关键论据，提前演练导师的“灵魂追问”。

### 3. 方法维护工作台
* **`learning-method-workbench`**：**学习方法工作台**。根据你的学科背景与个人偏好，灵活调优教学节奏、提示词风格或笔记沉淀规则。

---

## ⚡ 快速上手

### 1. 一键安装技能

你可以通过标准包管理器安装，也可以直接离线复制到你的工作区：

#### 方式 A：使用标准安装器（推荐）
在终端中进入你的学习项目根目录，通过安装器选择并添加技能：

```powershell
# 交互式添加技能到你的项目（以 Codex 为例）
npx skills add "https://github.com/Chil1T/learning-foundation" --skill learning-entry --agent codex --copy
```

#### 方式 B：零依赖离线复制
直接下载本项目，将需要的技能文件夹复制到你客户端的标准技能目录（如 Codex 的 `.agents/skills/`）：

```powershell
# 复制单个技能到当前学习项目
$targetProject = (Get-Location).Path
Copy-Item -Path "./skills/learning-entry" -Destination "$targetProject/.agents/skills/learning-entry" -Recurse
```

### 2. 开箱即用的对话体验

安装后，直接在你的 AI 客户端（Codex / Claude Code / Antigravity 等）中用自然语言唤醒：

#### 场景 1：学习一个新概念
> “使用 `learning-entry`。我想搞懂 Python 的装饰器原理，我已经熟悉函数和闭包了。今天先用一个小例子帮我建立直觉，暂时不用写文件。”

#### 场景 2：攻克论文中的复杂公式
> “使用 `paper-deep-reader`。精读我这篇论文第 4 节的公式 (3)，重点帮我拆解它的物理假设与推导中间步，告诉我为什么能做这个近似。”

#### 场景 3：下周组会汇报推演
> “使用 `research-meeting-prep`。根据我这周的推导笔记，帮我梳理 10 分钟组会汇报的主线逻辑，并预演两个导师最可能会追问的漏洞。”

更多使用技巧请参考 [开始使用指南](docs/getting-started.md)。

---

## 🎯 核心设计哲学

Learning Foundation 坚守五项核心认知与协作原则：

1. **目的与授权清晰 (Purpose & Authorization)**：智能体默认只读分析；仅在获得明确指令时才写入文件，绝不擅自修改、重构或污染你的个人笔记。
2. **内容身份分明 (Content Identity)**：严谨区分学术原文客观事实、AI 的推导建议与用户自己的真实理解，绝不张冠李戴。
3. **证据相称性 (Evidence-Proportionate Mastery)**：“听懂了”不等于“真正掌握了”。核对时只评估学习者独立的推导与表达，拒绝用“填空式”或“附和式”虚假通过。
4. **无缝断点续接 (Resumable Continuity)**：随时可以合上笔记本电脑，断点记录会保留未决问题与原文行号，下次随时从断点唤醒。
5. **开放演化与免锁定 (Open & Extensible)**：没有私有服务端，不捆绑专有格式；支持纯文本、Markdown、Obsidian 与任意本地工具自由组合。

完整哲学阐述请阅读 [设计原则与可替换默认](docs/principles.md)。

---

## 🛠️ 生态与可选工具

Learning Foundation 本身只需要文本对话即可顺畅工作。如果你的工作流中已经使用了以下优秀工具，套件能自然与之无缝协同：

* **文档解析**：配合 [MinerU](https://github.com/opendatalab/MinerU) 提取复杂学术 PDF 中的高精度公式与排版。
* **本地笔记**：原生兼容 [Obsidian](https://obsidian.md) 与任意标准 Markdown 双链笔记库。
* **演示课件**：可配合 [Slidev](https://sli.dev) 将精读笔记一键导出为现代化交互式幻灯片。
* **行动追踪**：可将学习行动检查点无缝同步至 [Todoist](https://todoist.com)。

详细搭配建议见 [可选工具与替代路径](docs/optional-tools.md)。

---

## 📖 深入文档

* [开始使用指南 (Getting Started)](docs/getting-started.md)：覆盖零配置起步、接入已有笔记库与长线学习管理。
* [客户端兼容指南 (Compatibility)](docs/compatibility.md)：在 OpenAI Codex、Claude Code、Antigravity 等环境下的落位指引。
* [设计原则 (Principles)](docs/principles.md)：套件底层的认知科学与工程协作设计基石。
* [默认组合说明 (Default Preset)](presets/default.md) / [科研组合说明 (Research Preset)](presets/research.md)：组合搭配逻辑。
* [工程验证说明 (Validation)](docs/validation.md)：自动化测试套件与安全合规边界。

---

## 📄 开源许可

本项目采用 [MIT License](LICENSE) 开源协议。自由使用、自由定制、自由组合。
