# aicf_ui/dsn_bridge.py
# aicf-dsn 的软依赖桥接。
#
# 控制台里有一批接口要读「DSN 全局设置命名空间」（Config）与「外周资源池」
# （ASR / TTS），这些东西属于 aicf-dsn 仓库。拆仓之后 aicf-dsn 是**可选安装**的：
#
#   装了 aicf-dsn → 语音 / TTS / 全局设置面板功能完整；
#   没装         → 相关接口明确返回「未安装」，页面照常可用，不出现 500。
#
# 为什么不在每个调用点写 try/except ImportError：
#   11 处调用点各写一遍，早晚有一处漏掉，表现为「某个页面 500」而不是
#   「某个功能不可用」——排查成本高得多。统一在这里收口。

from __future__ import annotations

from typing import Any, Optional

#: 未安装时统一对外的说明（前端直接展示这句）
DSN_MISSING_HINT = "未安装 aicf-dsn（pip install aicf-dsn），该功能不可用"


def dsn_config() -> Optional[Any]:
    """返回 aicf-dsn 的 Config 类；未安装（或导入失败）时返回 None。"""
    try:
        from aicf_dsn.config import Config
    except Exception:  # noqa: BLE001 - 未安装 / 依赖缺失 / 配置自检失败都算不可用
        return None
    return Config


def dsn_resource_setup() -> Optional[Any]:
    """返回 aicf-dsn 的 resource_setup 模块；不可用时返回 None。"""
    try:
        from aicf_dsn.models import resource_setup
    except Exception:  # noqa: BLE001
        return None
    return resource_setup


def dsn_tts_profile_manager() -> Optional[Any]:
    """返回 aicf-dsn 的 TTSProfileManager 类；不可用时返回 None。"""
    try:
        from aicf_dsn.plugins.builtin.tts_profile import TTSProfileManager
    except Exception:  # noqa: BLE001
        return None
    return TTSProfileManager


def dsn_available() -> bool:
    """aicf-dsn 是否可用。"""
    return dsn_config() is not None
