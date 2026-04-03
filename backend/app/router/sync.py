"""
数据同步路由
POST /api/sync/push - 推送本地数据到云端
POST /api/sync/pull - 从云端拉取数据
GET  /api/sync/status - 获取同步状态
POST /api/sync/full - 执行完整同步
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from app.services import sync_service

router = APIRouter()


class SyncRequest(BaseModel):
    table_name: str
    data: dict = {}


class SyncResponse(BaseModel):
    success: bool
    synced_at: str
    message: str
    synced_count: int = 0
    pulled_count: int = 0


@router.post("/push", response_model=SyncResponse)
async def push_to_cloud(request: SyncRequest):
    """
    推送本地数据到云端
    将指定表的所有未同步变更推送到云端
    """
    try:
        result = await sync_service.push_to_cloud(request.table_name)
        return SyncResponse(
            success=result.get("success", True),
            synced_at=datetime.now().isoformat(),
            message=result.get("message", ""),
            synced_count=result.get("synced_count", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pull")
async def pull_from_cloud(table_name: str = Query(..., description="表名")):
    """
    从云端拉取数据
    从云端拉取最新数据到本地
    """
    try:
        result = await sync_service.pull_from_cloud(table_name)
        return {
            "success": result.get("success", True),
            "synced_at": datetime.now().isoformat(),
            "message": result.get("message", ""),
            "pulled_count": result.get("pulled_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full")
async def full_sync():
    """
    执行完整同步
    先推送本地变更，再拉取云端最新数据
    """
    try:
        result = await sync_service.full_sync()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def sync_status():
    """获取同步状态"""
    try:
        state = sync_service.get_sync_state()
        pending = await sync_service.get_pending_changes()

        # 按表分组统计待同步数量
        pending_by_table = {}
        for p in pending:
            table = p.get('table_name', 'unknown')
            pending_by_table[table] = pending_by_table.get(table, 0) + 1

        return {
            "synced": len(pending) == 0,
            "last_sync": state.get("last_sync"),
            "sync_direction": state.get("sync_direction"),
            "pending_count": len(pending),
            "pending_tables": [
                {"table_name": table, "pending": count}
                for table, count in pending_by_table.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending(table_name: str = None):
    """获取待同步的变更列表"""
    try:
        pending = await sync_service.get_pending_changes(table_name)
        return {"pending": pending, "count": len(pending)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
