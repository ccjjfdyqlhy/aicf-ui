# launcher.py
# AICF（Agent Infrastructure Cybernetics Framework）应用启动器。
#
# 项目根目录由 AICF 框架代码占领（infra/ = 基础设施与运行时管理，
# harness/ = Agent 核心）；具体应用以 AppBundle / App 包形式
# 存在于 apps/ 下。本启动器负责"选择并运行"某个应用。
#
# 入口选择优先级:
#   1. 启动参数  --app <name>
#   2. 配置文件  apps.yaml（{app: {entry: "apps.foo.entry", description: ...}}）
#   3. 环境变量  DSN_APP=<name>
#   4. 默认      dsn_ui
#
# 约定: 应用包 apps/<name>/ 提供 entry 模块，含 main() 可调用对象。

from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent
APPS_CONFIG = ROOT / "apps.yaml"

_DEFAULT_APP = "dsn_ui"

# 应用清单（若存在 apps.yaml 则以其覆盖）
#
# 拆仓后每个应用是**独立仓库、独立发行包**，这里只登记「入口模块名」。
# 是否可用由 _available() 判断：模块没装（pip install 不到）就当它不存在，
# 不会因为「少装了一个 app」而让 --list 直接崩掉。
APPS: dict[str, dict[str, Any]] = {
    "dsn_ui": {
        "entry": "aicf_ui.entry",
        "description": "现代化统一 Web 控制台与模型调度交互界面",
        "default": True,
    },
    "dsn": {
        "entry": "aicf_dsn.entry",
        "description": "DSN 语音陪伴应用（需 pip install aicf-dsn）",
    },
    "coding_agent": {
        "entry": "aicf_code.entry",
        "description": "终端编码助手（需 pip install aicf-code）",
    },
    "dsn_study": {
        "entry": "aicf_study.entry",
        "description": "学习助手：题库、模拟考试、知识图谱（需 pip install aicf-study）",
    },
}


def load_apps_config() -> None:
    """读取 apps.yaml 并合并进 APPS。

    合并语义（2026-10 调整）：
      * 新应用直接加入 APPS；
      * 已内置的应用，**只允许覆盖展示性字段**（description），但 entry 保持内置值。

    为什么不允许改 entry：内置清单里的 entry 是框架保证可用的路径；允许 yaml 改写它
    会让「改了配置就跑不起来」成为可能，而这种失败在 --list 阶段看不出来，
    要等到真正启动才暴露。此前用 setdefault 导致连 description 都改不了。
    """
    if not APPS_CONFIG.exists():
        return
    try:
        import yaml
    except ImportError:  # 无 PyYAML 时静默使用内置清单
        return

    try:
        data = yaml.safe_load(APPS_CONFIG.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - yaml 损坏不应阻断启动
        return

    for name, cfg in data.items():
        if not isinstance(cfg, dict):
            continue
        cfg.setdefault("entry", f"{name}.entry")
        existing = APPS.get(name)
        if existing is None:
            APPS[name] = cfg
        else:
            # 内置应用：仅覆盖描述，保留内置 entry 与 default 标记
            if cfg.get("description"):
                existing["description"] = cfg["description"]


def _available(module_name: str) -> bool:
    """入口模块是否可导入（装了对应发行包才有）。

    为什么用 find_spec 而不是直接 import：--list 不该因为某个 app 没装就炸；
    find_spec 不执行模块体，代价极低。
    """
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


def available_apps() -> dict[str, dict[str, Any]]:
    """只返回当前环境里装得上的应用。"""
    return {
        name: cfg
        for name, cfg in APPS.items()
        if _available(cfg["entry"])
    }


def resolve_entry(name: str) -> Callable[[], Any]:
    cfg = APPS.get(name)
    if cfg is None:
        raise SystemExit(
            f"未知应用: {name!r}\n可用: {', '.join(sorted(available_apps()))}")
    module_name = cfg["entry"]
    try:
        mod = importlib.import_module(module_name)
    except ImportError as exc:
        raise SystemExit(
            f"应用 {name!r} 未安装（{module_name}）：{exc}\n"
            f"请先 pip install {module_name.split('.')[0].replace('_', '-')}"
        ) from exc
    return getattr(mod, "main")


def list_apps() -> str:
    lines = []
    available = available_apps()
    for name, cfg in sorted(APPS.items()):
        marker = " *" if cfg.get("default") else ""
        if name not in available:
            lines.append(f"  {name:<14}   [未安装] {cfg.get('description', '')}")
            continue
        lines.append(f"  {name:<14}{marker}  {cfg.get('description', '')}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    load_apps_config()
    parser = argparse.ArgumentParser(
        prog="dsn-harness",
        description="AICF 应用启动器 — 默认启动 Web 控制台（aicf-ui）。",
    )
    parser.add_argument("--app", default=None,
                        help="要启动的应用名（默认 dsn_ui，可用 DSN_APP 环境变量覆盖）")
    parser.add_argument("--list", action="store_true", help="列出可用应用")
    parser.add_argument("app_args", nargs="*", help="透传给应用的参数")
    args = parser.parse_args(argv)

    if args.list:
        print(list_apps())
        return

    name = args.app or os.environ.get("DSN_APP") or _DEFAULT_APP
    sys.argv = [sys.argv[0]] + args.app_args
    entry = resolve_entry(name)
    entry()


if __name__ == "__main__":
    main()
