"""Pytest全局配置和fixtures.

提供测试所需的共享资源和依赖注入.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir():
    """创建临时目录."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_stock_line():
    """示例股票信号行."""
    return "600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G"


@pytest.fixture
def sample_stock_lines():
    """多行示例股票信号."""
    return """600176\t中国巨石\t2026-03-02 11:21\t28.10\t 3.92%\t69\tBBIHTM_G
300861\t美畅股份\t2026-03-02 13:19\t18.78\t-1.26%\t15\tBBIHTM_G
002734\t利民股份\t2026-03-03 10:26\t21.03\t-2.55%\t261\tBBIHTM_G"""
