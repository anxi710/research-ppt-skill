# Optional image generation / 可选生图配置

## Runtime contract

Use a small number of generated concept illustrations when they explain the agreed
topic better than an available source image or native diagram. Match the accepted
palette, composition and visual style; generation is optional, not a requirement for
every page. Keep real task screenshots, published figures, data charts and generated
illustrations distinct. Never generate or redraw empirical evidence, fabricate a
benchmark interface, or give a generated image a paper citation.

Before use, discover the host's actual image tools and read their current instructions.
Prefer an available native tool; otherwise use an already configured provider/API
within the user's authorized data and spending scope. Configuration guidance alone
does not authorize installation, credential changes, uploads or paid test calls.
If unavailable, report the capability gap and use source images or native diagrams.

Register source evidence as `original_figure` or `source_table`, external context
images as `context_illustration`, and generated art as `generated_concept`.
Keep original-source provenance for source images. For generated art, record
provider/tool, requested and returned model when known,
prompt/reference hashes, generation date, local output/hash, intended purpose and
review observations. Link it to an `illustration` evidence entry and keep factual
explanation separately source-linked. Snapshot any input reference bytes through the
source or asset inventory; a reference path in free-form metadata alone does not bind
the file to the handoff. These describe the asset's origin, not evidence strength.
Label concept illustrations in the plan/notes and visibly where confusion is likely.
Inspect the image for scientific errors, invented text, inconsistent style and visual
clutter before handoff; inspect its crop and legibility again in the final PPTX.

## 选择接入方式

下面三种方式均用于准备图片素材，PPT 排版与导出仍交给 ppt-master。
先让 Agent 检查工具，再选择一条可用路径：

| 方式 | 适用情况 | 需要配置什么 |
|---|---|---|
| Codex 内置生图 | 当前会话提供 imagegen skill 和实际生图工具 | 通常直接自然语言调用；由宿主管理工具与模型 |
| Claude Code 工具调用 | 使用 Claude Code，已有可用生图 MCP，或允许 Bash 调用图片 API | 真实 MCP 服务，或下节的 Python SDK 与 API key |
| 直接调用图片 API | 希望明确指定模型、参数、输出与费用归属 | 官方 SDK、`OPENAI_API_KEY`、账号可用的图片模型 |

**能力与模型核验日期：2026-10-15。** 模型、工具和账号权限会变化，配置前应重查下方官方来源。
本 skill 不附带生图服务、MCP 服务或 API 凭证，也不会因为读取本指南就自动安装或付费调用。

## Codex：优先使用已有 imagegen

在 Codex 会话中可以使用下面的提示词。先确认工具可用，再执行用户已授权的生成：

> 读取 `./skills/research-ppt/SKILL.md` 及其同目录下的 `references/image-generation.md`。
> 检查本会话是否提供 imagegen skill 和生图工具。若可用，使用 `$imagegen` 为这次汇报
> 生成一张概念插图；沿用 style_profile.json 的配色和画风，不画实验数据，不加入文字、
> 品牌或人物身份。将图片保存到本次私有工作区的 assets/generated/，登记生成信息并检查。

官方文档支持在交互会话中用 `$imagegen` 显式调用；文档当前说明内置生图使用
`gpt-image-2`。工具的实际可用性以当前会话为准，内置图片模型由宿主管理；改变 Codex
主模型不等于切换图片模型。若缺少工具，可采用下方 API 路径，不能假设存在
`codex image` 之类的命令。[Codex 官方生图说明](https://learn.chatgpt.com/docs/image-generation)

## Claude Code：通过工具或 API 生图

Claude Code 可以编排外部工具；这里使用图片服务来产出像素文件，不把 Claude 的普通
文本回复当作图片生成接口。最少配置的做法是在已授权的 Bash 工具中运行下节 Python
示例，使用相同的 `OPENAI_API_KEY` 环境变量。无需为了单次调用额外安装 MCP。

若已经选定一个可信、实际存在的生图 MCP 服务，按该服务的安装说明配置，不能把
`/v1/images/generations` API 地址直接当成 MCP 地址。下面只是本地 stdio 服务的配置形状，
两个路径必须换成已安装服务的真实解释器和入口：

```bash
claude mcp add --transport stdio --scope local research-images -- \
  /absolute/path/to/python /absolute/path/to/installed_image_server.py
claude mcp get research-images
```

在 Claude Code 中用 `/mcp` 检查连接和实际工具列表。服务需要 key 时，优先从启动它的
环境读取；可移植的 `.mcp.json` 可引用 `${OPENAI_API_KEY}`，不写入真实值。
项目作用域可能需要用户批准加载。CLI 显示配置已添加，不代表服务已连接或生图成功。
[Claude Code MCP 文档](https://code.claude.com/docs/en/mcp)

本 skill 可通过路径直接读取。需要自动发现时，按 Claude Code 的 skill 目录约定安装；
不要仅为调用一次图片 API 改写本仓库的共享配置。
[Claude Code skills 文档](https://code.claude.com/docs/en/skills)

## API：显式指定 GPT Image 模型

以下命令面向 Bash，在你选择的 Python 3.11 环境中执行。SDK 是可选依赖，不加入普通
PPT 准备工具的必需依赖。密钥保留在个人环境或系统密钥管理中，不粘贴到对话、文档、
Git 或命令参数里。[官方 SDK 安装说明](https://developers.openai.com/api/docs/libraries)

```bash
python -m pip install --upgrade openai
read -rsp 'OpenAI API key: ' RESEARCH_PPT_API_KEY
export OPENAI_API_KEY="$RESEARCH_PPT_API_KEY"
unset RESEARCH_PPT_API_KEY
```

当前官方图片指南列出 `gpt-image-2.5-flare` 与 `gpt-image-2.5-sunburst`；下面使用前者。
先确认账号有相应权限和费用额度；模型 ID 是图片模型，不是 Codex 或 Claude 的主模型。
单张概念插图可以直接使用 Image API，复杂多轮流程也可使用 Responses 的生图工具。
[官方图片指南](https://developers.openai.com/api/docs/guides/image-generation)

把下面示例保存为本次私有工作区中的 `generate_concept.py`，准备一个 UTF-8
`prompt.txt`。脚本每运行一次都会请求生成一张图片；仅在授权调用后运行：

```python
import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--prompt", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
args = parser.parse_args()
prompt = args.prompt.read_text(encoding="utf-8")
if args.out.exists():
    raise SystemExit("Output exists; choose a new revision path.")
result = OpenAI().images.generate(
    model=args.model, prompt=prompt, n=1,
    size="1536x1024", quality="medium", output_format="png",
)
payload = result.data[0].b64_json
if not payload:
    raise SystemExit("No image returned; inspect the provider response.")
image = base64.b64decode(payload)
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_bytes(image)
record = {
    "kind": "generated_concept", "provider": "OpenAI Image API",
    "requested_model": args.model, "prompt": prompt,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "path": str(args.out), "sha256": hashlib.sha256(image).hexdigest(),
    "review_status": "pending",
}
args.out.with_suffix(".provenance.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8",
)
```

例如在该私有工作区目录中运行：

```bash
python generate_concept.py --model gpt-image-2.5-flare \
  --prompt prompt.txt --out assets/generated/background-01.png
```

请求形状与 base64 输出处理依据
[官方 Images Python 接口](https://developers.openai.com/api/reference/python/resources/images/methods/generate)。
示例只保存图片和待审记录，不会自动加入 PPT，也不代表科学检查已通过。

## 提示词与风格复用

沿用本次 style_profile.json：主体、场景与图的用途写清楚，固定配色、画法、视角与留白；
用一张已审过的概念插图作为后续风格参考时，记录其路径和 hash。不要模仿参考演讲者身份，
也不要为了统一风格改画原论文的结果图。中文标签、术语和数字优先由 ppt-master 用原生
文本叠加，保证整套字体、字号和可编辑性。

可作为起点的提示词（将概念替换为实际需要讲解的内容）：

> 为科研组会画一张“多步骤任务执行”的概念插图：一个任务经过三个连续工作阶段，
> 每阶段都留下可检查的成果。白色背景、深灰轮廓、单一蓝色 #2F5597 点缀，简洁扁平画法，
> 保留外围留白。不要文字、数字、坐标轴、实验结果、品牌标志或真实软件界面。

先生成必要的一张并检查，再决定是否扩展。同一套 PPT 可以同时使用原始证据图、外部
背景图、原生机制图和少量生成插图；无需把所有页面或图像统一成生成图片。

## 核验范围

本指南编写时只读核验了当前会话的生图工具可见性、Codex CLI 0.162.1 和 Claude Code
2.1.300 的 MCP 配置帮助，以及示例 Python 的离线语法。没有安装 SDK/MCP、设置真实
密钥或调用付费模型；具体服务连接、账户模型权限和生成效果需在使用时验证。
