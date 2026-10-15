# Research PPT Skill：通用科研汇报制作技能

[English](README.md) · [技能入口](skills/research-ppt/SKILL.md) · [运行手册](docs/runbook.md)

**本技能管“讲什么、如何讲、是否讲对”；ppt-master 管“把它做成 PPT”。**

适用于论文组会、文献综述、方法教学、研究进展和学术汇报。它是一套供具有
文件读取、代码执行和图片查看能力的 Agent 使用的技能，不是已部署的在线服务。

## 分层，而不是复制一个 PPT 生成器

| 本技能负责 | 交给 ppt-master |
|---|---|
| 核对论文版本、读懂方法与实验、建立证据记录 | 按当前版本选择制作路径 |
| 分析受众、补充必要基础、安排叙事和时间 | 页面设计与原生对象制作 |
| 提取参考模板风格，准备和核查原图 | PPTX、备注等实际导出 |
| 给每页定义一个问题、一幅核心视觉和结论边界 | 按修改单局部修复与重新导出 |
| 对最终 PPTX 做事实、视觉、结构校验 | 后端自己的技术检查 |

不再携带旧版 ppt-master 适配器，不绑定历史命令。子模块跟踪上游 `main`，
每次新制作任务开始前检查更新并读取当前说明。单次任务记录实际提交，制作中途不
悄悄升级。**Git 子模块必然记录一次提交；跟踪最新是更新策略，不是永远没有提交号。**

## 使用

正式发布后，使用 `git clone --recurse-submodules <仓库地址>` 获取。
下载离线发布包时，先在包根目录运行 `python scripts/restore_git.py` 恢复 Git 历史。

```bash
python -m pip install -r requirements.txt
python scripts/upstream.py update
python scripts/upstream.py status
```

让工具型 Agent 读取 `skills/research-ppt/SKILL.md`，并提供源论文、受众、时长、
语言和可选模板。默认不假定学校、学科、颜色、语言、页数或汇报人。
`profiles/academic-blue.json` 是可选的通用蓝白风格，不包含任何机构标识。

父技能先复用已提供的信息，只分批追问缺失或矛盾的关键要求，再汇总目的、受众与
基础、时长及 Q&A、语言、风格、结构重点和交付物。用户确认后才开始实质性的证据
准备和叙事设计；用户也可以明确授权“按这些要求开始”或委托 Agent 决定指定事项，
无需重复确认。普通的“帮我做 PPT”不视为委托。父技能确认不代替后端自己的必经关卡。

初始化私有工作区、补齐 `brief.json` 后，运行
`python skills/research-ppt/scripts/workflow.py intake --project <工作区路径>`
生成待确认的需求快照。脚本不会代替用户确认；Agent 只能根据真实回复记录确认或
委托及对应原话/可追溯引用。准备校验和交接会阻止未确认或已经过期的需求快照。

可以直接这样发任务：

> 请使用 Research PPT Skill 制作本次上传论文的组会 PPT。时长 25–30 分钟，
> 面向 AI 研究人员但不是论文子方向。按背景、问题、方法、实验、结论与分析组织。
> 先准备证据、必要基础知识、原图、风格和逐页方案，再交给当前版本的 ppt-master
> 制作。每页围绕一个主题与核心视觉，正文少字，讲稿充分。制作后真实渲染全部页面，
> 包括隐藏备答，检查并修复图例裁切、错位、数字和结论等问题，再交付。

## 仓库内容

- `skills/research-ppt/`：独立技能包，含核心指令、阶段参考、模板和准备/校验脚本。
- `third_party/ppt-master`：真实 Git 子模块，跟踪上游，不复制其实现。
- `scripts/`：更新子模块、检查公开文件、恢复 Git 历史和发布仓库的辅助脚本。
- `tests/`、`examples/synthetic/`：纯合成回归测试，不包含私人论文和模板。
- `.github/`：CI、Dependabot 更新配置、问题反馈模板。

证据与素材处理、叙事设计、视觉判断仍然是 Agent 工作。程序检查通过不代表论文结论
或视觉呈现自动正确；没有实际渲染与逐页核查时，只能交付标明未验证的草稿。

## 公开发布

在已登录 GitHub CLI、可访问 GitHub 的环境中：

```bash
gh auth login
python scripts/publish_github.py --repo research-ppt-skill --publish
```

脚本会确认当前账号，检查公开文件，更新子模块，运行本地测试，然后创建公开仓库并
推送。不覆盖同名仓库，不强推、不删除远端，不从聊天中索取 token。
默认不带 `--publish` 只打印计划，不执行网络写操作。详见 [发布说明](docs/publication.md)。

## 协议与更新

本项目原创指令与代码使用 **MIT**，与 ppt-master 当前根许可证一致。第三方论文、
图像、字体、模板、软件依赖仍保留各自协议，不因这个仓库 MIT 而自动变为 MIT。
公开仓库不携带个人资料、论文原图、校徽、旧汇报、字体或凭证。

Dependabot 配置用于在工作日检查子模块更新并提出 PR；它不是已启动的后台服务，
也不会自动合并。当前版本的实际兼容性需要新任务中的代表页验证。
