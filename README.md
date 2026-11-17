# aicf-ui

> **The local Agent console.** Manage models, run conversations and watch resource usage — everything on your own machine.

[English](README.md) · [中文](README_zh.md) · [底层库 aicf-core](https://github.com/ccjjfdyqlhy/aicf-core)

---

## 🚀 Three commands

```bash
git clone https://github.com/ccjjfdyqlhy/aicf-ui.git && cd aicf-ui
pip install -e .
python -m aicf_ui.server --port 8888
```

Then open <http://127.0.0.1:8888> and fill in **Settings → Provider** (Base URL + API Key).
No API key yet? The console still starts — you can look around.

---

## ✨ What you get

| You want to… | Where |
|---|---|
| Manage local + remote models in one place | **Models** page (llama.cpp / LM Studio / OpenAI-compatible) |
| Chat with a tool-using agent | **Chat** page (streaming, tool calls visible) |
| Watch VRAM, slots and per-session cost | **Resources** page |
| Ask a one-forward-pass question (System-1) | **Decide** page (yes/no, choice, score + probability) |
| Expose the console as an OpenAI-compatible backend | `API_MODE=passthrough` (see `aicf_ui/INTEGRATION_API.md`) |
| Use it from another client (Open WebUI / Continue / LangChain) | `aicf_ui/INTEGRATION_API.md` |

---

## 🔌 Dependencies

- **Required** — [`aicf-core`](https://github.com/ccjjfdyqlhy/aicf-core) `>=1.0,<2`: the agent kernel, model routing, tool protocol, context assembly and session store.
- **Model backend** — any OpenAI-compatible endpoint, or a local `llama-server` / LM Studio. No GPU required.
- **Optional** — [`aicf-dsn`](https://github.com/ccjjfdyqlhy/aicf-dsn) for voice / TTS panels (soft dependency: the console degrades instead of failing).

> **Note** — `aicf-core` 1.0.0 is not on PyPI yet (the published version is 0.6.1).
> For local development: `pip install -e /path/to/aicf-core`.

---

## 📁 Layout

```
aicf_ui/            the console package
├── server.py       FastAPI app: models, chat, resources, decide
├── agent.py        agent runtime wiring
├── engine.py       orchestrator + workspace bootstrap
├── config.py       UIConfig (ports, data dir, model profiles)
├── dotenv_boot.py  .env discovery
└── static/         pre-built frontend (the SvelteKit source is not shipped)
tests/              ported from the monorepo
main.py             launcher for the whole AICF app suite
installer.py        one-command installer (venv + deps + first run)
```

---

## 🧪 Development

```bash
pip install -r requirements.txt
pip install pytest
python -m pytest -q tests/
```

---

## 📄 License

Apache-2.0
