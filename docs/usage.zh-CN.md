# 使用指南

[English](usage.md) · [仓库首页](../README.zh-CN.md) · [Agent 运行手册](runbook.md)

本指南按“第一次使用”和“后续使用与维护”说明每一步的作用、操作与完成标志。环境配置可以交给 Agent 按[独立指引](../skills/research-ppt/references/environment-setup.md)执行；需要逐条材料处理、渲染和验收命令时，查阅运行手册。

环境准备可以由你或 Agent 完成；需求整理、文件维护、制作交接和审查通常由 Agent 执行，你负责提供材料、回答缺项并确认需求。默认提议制作详细研究报告，按主题或问题整合所给论文、笔记、实验结果、数据、图表和报告；明确指定时也可制作单篇论文汇报。以下命令使用已选定的 Python 3.11 环境。

以下示例在 `cd research-ppt-skill` 后从仓库根目录运行。将 `<path-to-material>` 替换为实际材料目录，可使用绝对路径或相对路径。

Agent 在任何 `cd` 之前先记录本次请求工作目录的绝对路径，并以此解析相对的技能入口和材料路径。默认产物根目录以此为准，不随技能安装位置变化。Agent 定位真实技能与脚本后，内部使用解析后的绝对路径；在其他目录运行时也可直接提供绝对入口和材料路径。实际请求位于其他目录时，在原目录用解析后的绝对脚本路径运行 `init`，或切换目录后通过 `--project` 传入原请求目录下的绝对工作区路径，并使用解析后的材料路径。以下任务示例以仓库根目录作为请求目录，使用已被 Git 忽略的 `./outputs/`。

## 第一次使用

### 步骤 1：获取仓库并安装辅助依赖

**作用：** 获取父技能、配套资源及 ppt-master 子模块，并让准备和校验脚本能够运行。

**操作：** 克隆完整仓库，进入目录后安装依赖。

```bash
git clone --recurse-submodules <仓库地址> research-ppt-skill
cd research-ppt-skill
python -m pip install -r requirements.txt
```

**完成标志：** `skills/research-ppt/` 和 `third_party/ppt-master/` 均已获取，辅助依赖安装完成。`requirements.txt` 只覆盖父技能的辅助工具，后端环境在下一步准备。

### 步骤 2：准备制作后端和渲染环境

**作用：** 确定本次实际使用的后端版本，并具备导出与检查真实 PPTX 的条件。

**操作：** 在新任务开始前检查更新，再查看实际路径、提交和入口文件。

也可以让 Agent 读取 `./skills/research-ppt/references/environment-setup.md`，按[环境配置指引](../skills/research-ppt/references/environment-setup.md)完成环境检查、安装和验证，再返回所选 Python、后端版本、渲染器及测试结果。README 中提供了可直接改写的调用示例；从其他目录发起时也可提供该指引的绝对路径。

```bash
python scripts/upstream.py update
python scripts/upstream.py status
```

按输出定位后端，读取其当前 `AGENTS.md` 和技能入口，再按这些说明安装后端依赖。准备真实 PPTX 渲染器；本技能的 `render-pptx` 使用 LibreOffice/soffice。`status` 只检查本地状态，不会拉取更新；网络失败时记录实际版本与限制，不把它称为“最新”。

也可以将完整的
`research-ppt` 技能目录复制或软链接到工具的技能发现目录；单独安装时明确提供后端路径。
不能只复制 `SKILL.md`，阶段参考、脚本和模板也是技能的一部分。

**完成标志：** 实际后端路径和提交已知，当前入口已阅读，依赖与真实渲染条件已检查。该版本在本次制作和复查过程中保持不变。

### 步骤 3：向 Agent 描述本次汇报

**作用：** 让 Agent 知道要向谁讲、讲到什么程度、用多长时间，以及交付什么。

**操作：**

让具有文件读取、代码执行和图片查看能力的 Agent 读取
`./skills/research-ppt/SKILL.md`，并提供材料文件或文件夹及研究主题／问题。
说明听众是谁、已有何种基础、汇报目的、详略程度、总时长与问答安排、语言、风格或参考模板、
结构重点和交付物。通常由 Agent 创建工作区并维护 JSON，你无需手写这些记录；材料清点、
选择和综合是 Agent 的工作，辅助脚本只负责组织和校验，不自动理解文件夹或生成研究结论。

下面是一段可直接改写的任务，把路径和要求替换为本次汇报的实际信息：

> 请读取 `./skills/research-ppt/SKILL.md`，
> 根据 `<path-to-material>` 制作详细研究报告 PPT。先清点其中的论文、阅读笔记和我的
> 实验结果，再围绕研究问题组织。面向了解基础机器学习、但不熟悉本方向的 AI 研究人员，
> 讲清必要背景、问题、机制与方法、证据、比较综合、局限，以及有材料支持的个人进展与下一步。
> 区分文献结论、我的结果和分析，标出证据缺口。总时长 25 分钟，包含 5 分钟 Q&A。
> 使用中文，保留英文技术术语；风格简洁学术，正文少字，使用原图、详细讲稿和隐藏备答页。
> 交付 PPTX、PDF 和讲稿。请先汇总需求让我确认，再开始证据准备。

新需求默认提议 `presentation_type: research_report` 和 `detail_level: detailed`；
也可明确选择单篇论文汇报、文献综述、进展汇报或方法教学，以及标准或概览深度。
上述时长、语言和结构只是示例。技能不默认学校、学科、语言、页数或汇报人。
未指定其他风格时，采用内置 Academic Navigator 模板，英文默认 Times New Roman、
中文默认 Microsoft YaHei（微软雅黑），保持统一字号角色、单强调色、
章节导航、信息封面、标题线、右下当前页码和图文分组；章节与布局随本次内容调整。
可明确选择其他模板或风格，包括可选的
[`academic-blue.json`](../skills/research-ppt/profiles/academic-blue.json)。
“简洁学术”或“设计由你决定”本身不表示放弃默认模板。

父技能先复用已有信息，只分批追问缺失或矛盾的关键要求，再展示易读的需求摘要。
用户确认后才开始实质性的证据准备和叙事设计。也可以明确说“按这些要求开始，
配色和页数由你决定”，委托指定事项，无需重复确认；普通的“帮我做 PPT”不视为委托。
关键需求变化后需要重新确认，父技能确认也不代替后端自己的必经关卡。
只依据所给材料，缺少证据时标出缺口，不编造结果、不自动扩展研究。

**完成标志：** 源文件可用，受众、时长、语言等核心信息足够用于初始化；最终需求将在步骤 5 汇总确认。

### 步骤 4：创建私有工作区，生成 `brief.json`

**作用：** 集中保存本次汇报的输入副本、来源指纹、需求记录与产物，并保持不同汇报的记录独立。

**操作：**

`brief.json` 是**每次汇报工作区里的需求文件，由 `init` 生成**。Agent 先从已提供的
主题或来源标题概括简短、描述性的项目名，不必为命名提前阅读实质证据，也不能加上
没有依据的研究结论。项目名应是安全的单个路径名，可以保留中文。以下命令以仓库
根目录为本次请求目录，创建新的**私有工作区**；运行前将引号内的材料占位路径替换为实际路径：

```bash
python ./skills/research-ppt/scripts/workflow.py init \
  --name 课题研究汇报 \
  --source "<path-to-material>/paper-a.pdf" \
  --source "<path-to-material>/paper-b.pdf" \
  --source "<path-to-material>/reading-notes.md" \
  --source "<path-to-material>/experiment-results.csv" \
  --presentation-type research_report --detail-level detailed \
  --minutes 25 --language zh-CN \
  --audience "了解基础机器学习，但不熟悉本方向的 AI 研究人员"
```

不传 `--project` 时，命令默认在执行目录的 `./outputs/<安全项目名>/` 创建工作区，
并打印实际路径。例如当前目录为 `/workspace/research-ppt-skill` 时，文件会出现在
`/workspace/research-ppt-skill/outputs/课题研究汇报/brief.json`。后续命令应使用实际
打印的路径，替换下文示例。同名新项目自动加 `-02`、`-03` 等后缀，不覆盖旧目录，
也不会默认为继续旧汇报。显式 `--project` 优先，并应指向新的空工作区；相对路径仍以
执行命令时的目录为准。用户指定的目录或文件名始终优先。

Agent 负责提供概括后的 `--name`；省略时，辅助脚本只回退到来源文件的文件名主体，
不会做语义概括。用户提供文件夹时，Agent 先清点并选择能读取的相关材料，对每个选定文件
重复传入 `--source`；该参数只接收文件，不接收目录。参考模板可加
`--template /path/to/reference.pptx`。初始化仅复制文件、计算 SHA-256，不阅读或综合内容。

普通来源初始角色为 `research_source`，参考模板为 `style_reference`。Agent 随后按实际用途
调整每项来源的 `role`：`research_source`（研究来源）、`reading_note`（阅读笔记）、
`user_result`（个人结果）、`background_reference`（背景参考）、`style_reference`（风格参考）。
保留实际生成的来源 ID、路径和哈希，不要用示例值覆盖；来源角色一并纳入步骤 5 的确认。

中间文件也保存在同一工作区。默认成品名为 `exports/课题研究汇报.pptx`、
`exports/课题研究汇报-preview.pdf`、`exports/课题研究汇报-notes.md`，只生成用户要求的格式。
可选的 `project_name` 与 `output_files` 字段记录命名默认值和显式覆盖，不代表需求已获确认。
这些文件属于私有任务材料，即使位于仓库内已忽略的 `outputs/`，也不能提交或公开。

**完成标志：** 工作区根目录已有 `brief.json`，`inputs/` 中已有输入副本。此时需求确认仍为待确认，不能把初始化成功视为已同意全部需求。

可选演示：运行 `python examples/synthetic/prepare.py --out outputs/synthetic-research-report-demo`，再打开 `outputs/synthetic-research-report-demo/brief.json`，即可不提供论文先查看实际文件。它使用短小的合成方案和用于测试的虚构确认，不代表真实授权，也不会制作 PPT。

### 步骤 5：补齐并确认需求

**作用：** 把对话中的要求转成可追踪的制作约定，避免受众、时长、风格等关键选择被默默更改。

**操作：** Agent 根据对话补齐 `brief.json`，保留步骤 4 生成的来源记录，并记录源文件的确切版本。

仓库中提供了完整的[合成 `brief.json` 示例](../skills/research-ppt/templates/brief.example.json)。
其中来源哈希对应虚构的教学输入，确认状态仍为待确认；实际任务应使用 `init` 生成。
以下是上述汇报的部分需求字段：

```json
{
  "presentation_type": "research_report",
  "detail_level": "detailed",
  "audience": "了解基础机器学习，但不熟悉本方向的 AI 研究人员",
  "target_minutes": 25,
  "qa_time_included": true,
  "qa_minutes": 5,
  "language": "zh-CN",
  "purpose": "讲清研究问题、方法、证据、综合分析和个人进展",
  "sections": ["背景", "问题", "方法", "证据", "综合分析", "局限", "进展与下一步"],
  "style_intent": "简洁学术，使用来源原图，正文少字，无机构标识",
  "deliverables": ["pptx", "pdf", "speaker_notes"]
}
```

这里的 25 分钟包含 5 分钟问答，因此正文讲述时间为 20 分钟。初始化默认的问答是否计时尚未确定，风格也待补充；汇报类型与详略同样是待接受的提议。Agent 可在确认前修改 `presentation_type` 和 `detail_level`，两项存在时会纳入需求快照。旧需求文件没有这两项仍然有效，不得为套用新默认值而静默改写。填好后再执行：

```bash
python ./skills/research-ppt/scripts/workflow.py intake --project outputs/课题研究汇报
```

命令在 `brief.json.intake_confirmation` 中生成**待确认**的需求快照，由 Agent
展示给用户。收到真实确认或已有覆盖相关选择的明确委托后，才能将 `status` 记为 `confirmed` 或 `delegated`，
并在 `user_response` 中记录实际指令的原话或可追溯引用。脚本不会代替用户确认，准备校验和
交接会阻止未确认或已经过期的快照。

**完成标志：** 用户已接受需求摘要，或已有覆盖相关选择的明确授权；确认记录包含实际回复，且需求快照与当前 `brief.json` 一致。

### 步骤 6：准备证据与逐页方案，生成制作交接

**作用：** 把确认后的要求落实为有来源依据的内容和逐页任务，向后端交付完整、可核对的准备材料。

**操作：** Agent 阅读材料、检查原图，建立证据和图表来源记录，按研究问题而非文件顺序组织叙事，完成风格和逐页方案。每条关键结论可追溯到具体来源，区分文献结论、自己的结果和汇报者分析；笔记可以辅助阅读，不能在缺少原文时充当已发表结论的证明。材料矛盾或证据缺失时明确标出。

保留 `init` 生成的 `design_contract_version` 和样式约定。默认导航已开启，Agent 必须
填写实际章节、页归属和封面豁免；保留模板绝对路径，将已决定采用的
`template_reference.status` 记为 `selected`。导航未规划、模板仍待决或默认规范缺失时，
预检会拒绝交接。不同风格仅依据真实用户选择记录 `user_override`，不把自由排版视为默认。

详细报告讲清必要背景、问题、机制与方法、证据、比较综合和局限；个人进展与下一步以所给材料为依据。正文适配约定讲述时间，支撑细节放入充分讲稿和真正隐藏的备答页，不固定页数，也不靠塞满文字增加详细程度。准备好后执行：

```bash
python ./skills/research-ppt/scripts/workflow.py preflight \
  --project outputs/课题研究汇报 --out outputs/课题研究汇报/qa/preflight.json
python ./skills/research-ppt/scripts/workflow.py handoff \
  --project outputs/课题研究汇报 --run-id run-01
```

只做初始化的工作区不会通过；`preflight` 通过也不代表程序已经理解研究材料。Agent 仍须核对证据与设计。每次交接使用新的运行编号，已有交接快照不能覆盖。

**完成标志：** 准备预检通过，`handoff/run-01/` 中已有带校验指纹的准备快照、默认模板副本及制作说明。此时产物是交接材料，实际 PPTX 在下一步制作。

### 步骤 7：制作、独立审查并交付

**作用：** 将方案做成实际 PPT，并确认最终文件的科学内容、可读性和导出效果符合要求。

**操作：** Agent 将交接材料映射到步骤 2 所记录版本的 ppt-master，完成其当前必经关卡，先检查代表页再扩展制作。导出后真实渲染最终 PPTX，逐页检查并修复，覆盖隐藏备答页；修改后的文件使用新的渲染和审查记录。

默认路线把交接中的模板根目录交给后端，完成实际选择、安装及应用记录。
制作回执保留模板指纹、实际安装文件及应用说明；独立审查从真实渲染核对新版设计。
仅写模板名称、复制配色或把 `applied` 改成真值不能通过验收。

交付的 `-preview.pdf` 是最终 PPTX 可见页的真实渲染；隐藏备答页仍须纳入独立的全页渲染和审查。

**完成标志：** 所请求的 PPTX、可见页 PDF、讲稿等文件实际存在，最终审查对应最终版本，并说明可编辑与栅格内容的范围。缺少真实渲染时标为未验证草稿。制作回执、渲染和验收命令见[运行手册](runbook.md)。

## 后续使用与维护

以下步骤按场景执行，不必在每次使用时全部重做。

### 步骤 1：开始另一场汇报

**作用：** 复用已安装的环境，同时保持不同汇报的材料和记录独立。

**操作：** 在没有进行中的制作或复查时，按首次使用步骤 2 检查后端更新；然后重复步骤 3–7，概括新汇报的项目名，重新确认本次受众、时长和其他要求。`init` 在本次请求目录的 `outputs/` 下创建新工作区；同名时自动加编号，后续使用命令实际打印的路径。

**完成标志：** 新工作区拥有自己的输入、`brief.json`、交接和 QA 记录；上一场汇报的记录与成品仍可追溯。

### 步骤 2：继续或修改已有汇报

**作用：** 延续已确认的要求与正确内容，只处理本次变更及其影响。

**操作：** 告诉 Agent 原工作区路径和修改目标，让它恢复现有 `brief.json`、交接与 QA 记录，不重新运行 `init`。受众、时长、来源或其他关键要求变更时，只确认受影响的选择；准备材料变更时生成新交接，布局或导出问题交给后端定点修复。新 PPTX 重新渲染和审查，保留旧版本。

已有工作区和 `output_files` 路径继续有效，不为套用新的命名默认值而改写。

**完成标志：** 新版本及其审查记录对应本次变更，需求快照仍有效，已接受的旧版本没有被覆盖。

### 步骤 3：更新技能仓库与后端

**作用：** 获取通用技能和上游制作能力的更新，同时保留每次汇报所使用版本的可复现记录。

**操作：** 先用 `git status --short` 检查并妥善保存本地改动；只在工作区干净、没有进行中的制作或复查时更新：

```bash
git pull --ff-only
git submodule update --init --recursive
python scripts/upstream.py update
python scripts/upstream.py status
```

`git submodule update` 恢复父仓库记录的提交，`upstream.py update` 再跟踪上游 `main`。后端有未保存改动或提交指针尚未记录时，辅助脚本会拒绝继续更新；先审阅和保存，不强行丢弃。更新后重读当前入口，按其要求检查代表页；维护者审阅并记录接受的子模块指针。单次制作中途保持原版本，升级应开启新的构建与审查。详见[上游更新策略](upstream.md)。

**完成标志：** 采用的版本和变更已记录，当前入口已重读，代表页验证及已知限制已记载。

### 步骤 4：验证共享改动并积累通用改进

**作用：** 让技能、脚本或文档的修改有可复查的依据，并防止私人汇报材料进入公开仓库。

**操作：** 使用纯合成材料复现需要修复的问题，在已安装依赖的 Python 环境中运行：

```bash
python -m unittest discover -s tests -v
python scripts/check_repo.py
```

涉及渲染链路时可启用 `RUN_RENDER_TESTS=1` 执行真实渲染测试，并如实记录跳过项。提交前检查差异，不包含用户论文、私人模板、成品、凭证或字体文件。问题报告与回归要求见[贡献说明](../CONTRIBUTING.md)；本地检查通过不代表已验证所有后端版本或真实论文制作。

**完成标志：** 相关检查通过，实际测试范围和未覆盖内容已记录，共享改动仅包含可公开的通用内容。

私有工作区中，`brief.json` 与 `inputs/`、`analysis/`、`assets/`、`design/`、
`notes/`、`handoff/`、`production/`、`qa/`、`exports/` 并列。
这些是私有任务文件；仓库内的 `outputs/` 已忽略，不应提交或公开其中的材料。
