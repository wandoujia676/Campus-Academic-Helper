"""
测试模块
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_root():
    """测试根路径"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "LearnMate API"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health():
    """测试健康检查"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_video_notes_invalid_subject():
    """测试视频笔记 - 无效科目"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/video/notes",
            json={"url": "https://bilibili.com/test", "skill_type": "invalid"}
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_exam_scan_invalid_subject():
    """测试试卷扫描 - 无效科目"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/exam/scan",
            data={"skill_type": "invalid"}
        )
        # 没有文件时会返回422或500
        assert response.status_code in [422, 500]


@pytest.mark.asyncio
async def test_sync_status():
    """测试同步状态"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/sync/status")
        assert response.status_code == 200
        data = response.json()
        assert "synced" in data
        assert "pending_count" in data


@pytest.mark.asyncio
async def test_video_notes_list():
    """测试获取笔记列表"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/video/notes")
        assert response.status_code == 200
        data = response.json()
        assert "notes" in data


@pytest.mark.asyncio
async def test_exam_questions_list():
    """测试获取错题列表"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/exam/questions")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
