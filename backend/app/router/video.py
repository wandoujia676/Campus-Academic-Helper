"""
视频笔记路由
POST /api/video/notes - 生成视频笔记
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import video_service
import uuid

router = APIRouter()

class VideoNoteRequest(BaseModel):
    url: str
    skill_type: str  # 'adv_math' | 'ce'

class VideoNoteResponse(BaseModel):
    id: str
    status: str
    markdown: str
    metadata: dict
    exercises: list

@router.post("/notes", response_model=VideoNoteResponse)
async def create_video_note(request: VideoNoteRequest):
    """
    生成视频笔记
    流程: URL解析 -> 视频下载 -> 语音识别 -> AI章节分解 -> 生成笔记+练习题
    """
    if request.skill_type not in ['adv_math', 'ce']:
        raise HTTPException(status_code=400, detail="无效的科目类型")

    try:
        result = await video_service.process_video(
            url=request.url,
            skill_type=request.skill_type
        )
        return VideoNoteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes")
async def list_notes(skill_type: str = None):
    """获取笔记列表"""
    from app.database import get_db, dict_from_row
    conn = get_db()
    cursor = conn.cursor()

    if skill_type:
        cursor.execute(
            "SELECT * FROM notes WHERE skill_type = ? AND deleted = 0 ORDER BY created_at DESC",
            (skill_type,)
        )
    else:
        cursor.execute("SELECT * FROM notes WHERE deleted = 0 ORDER BY created_at DESC")

    notes = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return {"notes": notes}

@router.get("/notes/{note_id}")
async def get_note(note_id: str):
    """获取单个笔记详情"""
    from app.database import get_db, dict_from_row
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="笔记不存在")

    return dict_from_row(row)
