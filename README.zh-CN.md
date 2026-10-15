# Research PPT Skill：通用科研汇报制作技能

[English](README.md) · [技能入口](skills/research-ppt/SKILL.md) · [使用指南](docs/usage.zh-CN.md)

**本技能管“讲什么、如何讲、是否讲对”；ppt-master 管“把它做成 PPT”。**

面向基于所给材料的详细研究报告 PPT：Agent 可整合多篇论文、阅读笔记、你的实验结果、数据、图表和报告，围绕研究主题或问题组织内容，区分已发表结论、个人结果和汇报者分析。也支持明确指定的单篇论文组会、文献综述、进展汇报和方法教学。它是一套供具有文件读取、代码执行和图片查看能力的 Agent 使用的技能，不是已部署的在线服务。

## 分层，而不是复制一个 PPT 生成器

| 本技能负责 | 交给 ppt-master |
|---|---|
| 核对材料版本、读懂方法与实验、建立证据记录 | 按当前版本选择制作路径 |
| 分析受众、补充必要基础、安排叙事和时间 | 页面设计与原生对象制作 |
| 提取参考模板风格，准备和核查原图 | PPTX、备注等实际导出 |
| 给每页定义一个问题、一幅核心视觉和结论边界 | 按修改单局部修复与重新导出 |
| 对最终 PPTX 做事实、视觉、结构校验 | 后端自己的技术检查 |

子模块 `ppt-master` 跟踪上游 `main`，每次新制作任务开始前检查更新并读取当前说明。单次任务记录实际提交，制作中途不悄悄升级。**Git 子模块必然记录一次提交；跟踪最新是更新策略，不是永远没有提交号。**

## 使用

### 第一次使用

先获取仓库，再让 Agent 按[环境配置指引](skills/research-ppt/references/environment-setup.md)检查和安装依赖：

```bash
git clone --recurse-submodules <仓库地址> research-ppt-skill
cd research-ppt-skill
```

可直接把下面的话交给 Agent；以下相对路径以仓库根目录为基准：

> 请读取 `./skills/research-ppt/references/environment-setup.md`，按说明配置本项目环境，并报告依赖、后端和真实 PPTX 渲染的检查结果。

如需复用已有环境，可追加“请使用已有的 conda `docs` 环境”；环境名称由你选择。

环境准备好后，让 Agent 读取[技能入口](skills/research-ppt/SKILL.md)，并提供材料、受众、时长、语言与可选模板。例如：

> 请读取 `./skills/research-ppt/SKILL.md`，根据 `<path-to-material>` 中的论文、笔记和我的实验结果，围绕研究问题制作详细的中文研究报告 PPT。面向有机器学习基础的研究生，总计 25 分钟，含 5 分钟问答。区分文献结论、我的结果和分析，标出证据缺口。先汇总需求让我确认，再准备证据、制作并逐页检查，交付 PPTX、PDF 和详细讲稿。

将 `<path-to-material>` 替换为实际资料路径，可以使用相对路径或绝对路径。

可以直接提供资料文件夹。Agent 会清点相关材料，围绕研究问题组织完整汇报；正文适配约定时长，支撑细节放入详细讲稿和隐藏备答页，缺失证据明确说明。也可以明确要求单篇论文汇报等其他类型。

Agent 会从主题或来源标题概括简短项目名，默认在 `./outputs/<project-name>/` 保存私有工作区；所需成品在其中的 `exports/` 下命名为 `<project-name>.pptx`、`<project-name>-preview.pdf` 和 `<project-name>-notes.md`。你指定的文件名和目录优先。仓库内的 `outputs/` 已忽略，不应提交或公开。

由你确认需求或明确委托后继续；完整配置见[合成示例](skills/research-ppt/templates/brief.example.json)。制作后仍须真实渲染和审查最终 PPTX。

安装、需求确认、制作与验收的逐步说明见[首次使用指南](docs/usage.zh-CN.md#第一次使用)，每一步均保留作用、操作和完成标志。

需要少量风格一致的概念插图时，见[生图配置指南](skills/research-ppt/references/image-generation.md)，包含 Codex、Claude Code 和 API 三种方式。

### 后续使用与维护

- **新汇报或续作：** 新汇报用新工作区；已有汇报恢复原工作区，只确认变更。见[后续使用与维护](docs/usage.zh-CN.md#后续使用与维护)。
- **更新与检查：** 在制作任务之间更新版本，并验证共享改动。详见[维护步骤](docs/usage.zh-CN.md#后续使用与维护)和[上游策略](docs/upstream.md)。
- **查看具体命令：** [Agent 运行手册](docs/runbook.md)包含材料处理、渲染、审查和最终验收命令。

## 仓库内容

- `skills/research-ppt/`：独立技能包，含核心指令、阶段参考、模板和准备/校验脚本。
- `third_party/ppt-master`：真实 Git 子模块，跟踪上游，不复制其实现。
- `scripts/`：更新子模块、检查仓库文件的维护脚本。
- `tests/`、`examples/synthetic/`：纯合成回归测试，不包含私人论文和模板。
- `.github/`：CI、Dependabot 更新配置、问题反馈模板。

证据与素材处理、叙事设计、视觉判断仍然是 Agent 工作。程序检查通过不代表研究结论
或视觉呈现自动正确；没有实际渲染与逐页核查时，只能交付标明未验证的草稿。

## 协议与更新

本项目原创指令与代码使用 **MIT**，与 ppt-master 当前根许可证一致。第三方论文、
图像、字体、模板、软件依赖仍保留各自协议，不因这个仓库 MIT 而自动变为 MIT。
公开仓库不携带个人资料、论文原图、校徽、旧汇报、字体或凭证。

Dependabot 配置用于在工作日检查子模块更新并提出 PR；它不是已启动的后台服务，
也不会自动合并。当前版本的实际兼容性需要新任务中的代表页验证。
