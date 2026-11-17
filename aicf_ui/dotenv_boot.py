# aicf_ui/dotenv_boot.py
"""dsn_ui 的 .env 加载引导。

## 为什么需要单独一个模块

`aicf_ui/config.py` 里的 `UIConfig` 是**导入时求值**的类属性
（`HOST = os.getenv(...)` 之类）。一旦 `UIConfig` 被导入，环境变量再变也不会
影响它。因此 load_dotenv **必须发生在任何 `from aicf_ui.config import ...`
之前**，否则 .env 里的 `DSN_UI_*` 永远不生效。

## 之前的状况（2026-10 修复）

dsn_ui 全模块都不调用 `load_dotenv`，只有运行中惰性 import `apps.dsn.models`
时才被间接触发 —— 那时启动早期读到的变量早已定型。结果是「.env 里写了
`DSN_UI_PORT=9000`，控制台仍然起在 8888」，属于非常难排查的问题。

## 用法

任何 dsn_ui 的入口（`server.main()`、`__main__`、测试 fixture）都要在
导入 `aicf_ui.config` **之前**先 `import aicf_ui.dotenv_boot`。
更稳妥的写法是让入口模块第一行就 import 本模块。
"""

from __future__ import annotations

import os
from pathlib import Path

#: 仓库根目录（aicf_ui/ → apps/ → 仓库根）
#: 包根目录（aicf_ui/ 自身）
PACKAGE_ROOT = Path(__file__).resolve().parent

#: 兼容旧名：过去指向 monorepo 的仓库根。拆仓后没有"仓库根"这回事，
#: .env 的查找改成候选列表（见 _env_candidates）。
REPO_ROOT = PACKAGE_ROOT.parent.parent

_loaded = False


def _env_candidates() -> list[Path]:
    """.env 的查找顺序（先命中先用）。

    拆仓后应用不再依附某个仓库根目录，因此：
      1. AICF_ENV_FILE —— 显式指定；
      2. 当前工作目录的 .env —— 开发者最常用的位置；
      3. ~/.aicf/ui/.env —— 终端用户的位置；
      4. 包目录上一级 —— pip 安装后的兜底（通常不存在）。
    """
    candidates: list[Path] = []
    explicit = os.environ.get("AICF_ENV_FILE")
    if explicit:
        candidates.append(Path(explicit).expanduser())
    candidates.append(Path.cwd() / ".env")
    candidates.append(Path.home() / ".aicf" / "ui" / ".env")
    candidates.append(PACKAGE_ROOT.parent / ".env")
    return candidates


def load_env(override: bool = False) -> bool:
    """加载仓库根目录的 .env。幂等；python-dotenv 缺失时静默跳过。

    返回是否确实加载了文件。
    """
    global _loaded
    if _loaded and not override:
        return True

    env_path = None
    for candidate in _env_candidates():
        if candidate.is_file():
            env_path = candidate
            break
    if env_path is None:
        _loaded = True
        return False

    try:
        from dotenv import load_dotenv
    except ImportError:  # python-dotenv 未安装：退化为只读进程环境变量
        _loaded = True
        return False

    # override=False：进程环境变量优先于 .env，符合常见约定
    load_dotenv(env_path, override=override)
    _loaded = True
    return True


# 导入即加载：任何 `import aicf_ui.dotenv_boot` 都会完成这一步。
load_env()

__all__ = ["load_env", "REPO_ROOT"]
