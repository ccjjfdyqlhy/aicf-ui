# aicf-ui

> **本地 Agent 控制台。** 模型管理、对话、资源用量，全部跑在你自己的机器上。

[English](README.md) · [中文](README_zh.md) · [底层库 aicf-core](https://github.com/ccjjfdyqlhy/aicf-core)

---

## 🚀 三行上手

```bash
git clone https://github.com/ccjjfdyqlhy/aicf-ui.git && cd aicf-ui
pip install -e .
python -m aicf_ui.server --port 8888
```

然后打开 <http://127.0.0.1:8888>，在 **Settings → Provider** 里填 Base URL 和 API Key 就能开始聊。
还没申请 API Key？控制台照样能启动，先四处看看。

---

## ✨ 能做什么

| 你想… | 找谁 |
|---|---|
| 把本地模型和远程端点放一起管 | **Models** 页（llama.cpp / LM Studio / OpenAI 兼容） |
| 和会用工具的 Agent 对话 | **Chat** 页（流式输出，工具调用可见） |
| 看显存、槽位、单会话成本 | **Resources** 页 |
| 问一个「一次前向就能答」的问题（System-1） | **Decide** 页（yes/no、单选、打分 + 概率） |
| 把控制台当 OpenAI 兼容后端给别人用 | `API_MODE=passthrough`（见 `aicf_ui/INTEGRATION_API.md`） |
| 在 Open WebUI / Continue / LangChain 里用 | `aicf_ui/INTEGRATION_API.md` |

---

## 🔌 依赖

- **必须** — [`aicf-core`](https://github.com/ccjjfdyqlhy/aicf-core) `>=1.0,<2`：Agent 内核、模型路由、工具协议、上下文装配与会话存储。
- **模型后端** — 任意 OpenAI 兼容端点，或本地 `llama-server` / LM Studio。不需要显卡。
- **可选** — [`aicf-dsn`](https://github.com/ccjjfdyqlhy/aicf-dsn) 提供语音 / TTS 面板（软依赖：没装时相关功能降级而不是报错）。

> **注意** — `aicf-core` 的 1.0.0 还没发到 PyPI（线上是 0.6.1）。
> 本地开发可以 `pip install -e /path/to/aicf-core`。

---

## 📁 目录

```
aicf_ui/            控制台包
├── server.py       FastAPI 应用：模型、对话、资源、决策
├── agent.py        agent 运行时接线
├── engine.py       orchestrator 与工作区初始化
├── config.py       UIConfig（端口、数据目录、模型 profile）
├── dotenv_boot.py  .env 查找
└── static/         前端构建产物（前端源码不随仓发布）
tests/              从 monorepo 迁移过来的用例
main.py             AICF 应用套件的启动器
installer.py        一条命令安装（venv + 依赖 + 首次运行）
```

---

## 🧪 开发

```bash
pip install -r requirements.txt
pip install pytest
python -m pytest -q tests/
```

---

## 📄 许可证

Apache-2.0
