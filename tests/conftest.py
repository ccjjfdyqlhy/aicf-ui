# tests/conftest.py
# aicf-ui 的测试配置。
#
# 从 monorepo 的 tests/conftest.py 拆出来的部分：
#   1. 仓库未以包形式安装时，保证 `import aicf_ui` 可用；
#   2. 把「会写文件的数据目录」隔离到临时目录（DSN_UI_DATA_DIR）；
#   3. 每个用例后重置进程级单例（ModelOrchestrator / 本地引擎注册表）。
#
# 刻意**不**改变工作目录：部分用例用相对路径定位包内资源，
# cwd 一旦变成 tmp 就会大面积 FileNotFoundError。

from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# 保证 `import aicf_ui` 可用（仓库未以包形式安装时）
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_configure(config):
    """注册自定义 marker，并补齐「无 .env 也能收集」的最小环境。"""
    config.addinivalue_line("markers", "slow: 运行较慢的测试")
    config.addinivalue_line(
        "markers", "integration: 需要外部服务/设备/网络的测试"
    )

    # 占位 key：控制台的导入期检查发现「未配置」会拉起交互式引导，
    # 而引导要读 stdin —— 在 pytest 里会把整个收集过程挂死。
    # 测试全程不访问真实模型后端，这个值只是过导入关。
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy-not-real")

    # 日志：别往仓库 logs/ 里写测试流量。
    _tmp = tempfile.mkdtemp(prefix="aicf_ui_env_")
    os.environ.setdefault("LOG_DIR", str(Path(_tmp) / "logs"))


@pytest.fixture(autouse=True)
def _isolate_repo_state(monkeypatch):
    """隔离测试副作用：数据目录指向临时目录，并重置全局单例。"""
    tmp_path = Path(tempfile.mkdtemp(prefix="aicf_ui_test_"))

    # 控制台的数据目录：<db / 凭据密文 / 思考链缓存 / 设置覆盖> 都落在这里
    monkeypatch.setenv("DSN_UI_DATA_DIR", str(tmp_path / "dsn_ui_data"))

    try:
        yield
    finally:
        # 1) 清理进程级单例，避免用例之间串味
        try:
            from infra.orchestrator import ModelOrchestrator

            ModelOrchestrator.reset_instance()
        except Exception:  # noqa: BLE001 - 未导入该模块时无需清理
            pass
        # 2) 清空本地引擎子进程的全局注册表。
        #    背景：用例里用 mock 启动 launcher 会把它登记进
        #    infra.orchestrator.local_engine._ACTIVE_LAUNCHERS，而 atexit 的
        #    _cleanup_active_launchers() 会在 pytest 关闭输出流之后再去 stop()
        #    它们——既刷出一串 "Logging error"，又会对着永不退出的 mock 空等超时。
        try:
            from infra.orchestrator import local_engine

            for launcher in list(local_engine._ACTIVE_LAUNCHERS):
                local_engine._ACTIVE_LAUNCHERS.discard(launcher)
                with contextlib.suppress(Exception):
                    launcher.stop(timeout=0.1)
        except Exception:  # noqa: BLE001 - 未导入该模块时无需清理
            pass
        # 3) 删除临时数据目录
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def stub_client():
    """开箱可用的确定性模型客户端（离线测试用）。"""
    from infra.orchestrator import ChatResponse, StubChatClient

    return StubChatClient(responses=[ChatResponse(content="固定回复")])
