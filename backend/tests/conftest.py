"""
pytest配置
"""
import pytest
import sys
from pathlib import Path

# 确保backend目录在sys.path中
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
