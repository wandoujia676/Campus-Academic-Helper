"""
试卷扫描路由
POST /api/exam/scan - 扫描试卷识别错题
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services import exam_service
import uuid

router = APIRouter()

class ExamScanResponse(BaseModel):
    id: str
    status: str
    questions: list
    summary: dict

@router.post("/scan", response_model=ExamScanResponse)
async def scan_exam(
    file: UploadFile = File(...),
    skill_type: str = "adv_math"
):
    """
    扫描试卷图片，识别错题并分析
    流程: 图片预处理 -> OCR识别 -> 错题提取 -> AI归因分析 -> 存储
    """
    if skill_type not in ['adv_math', 'ce']:
        raise HTTPException(status_code=400, detail="无效的科目类型")

    if not file.content_type.startswith(('image/', 'application/pdf')):
        raise HTTPException(status_code=400, detail="只支持图片或PDF格式")

    try:
        # 读取文件内容
        content = await file.read()

        result = await exam_service.process_exam(
            file_content=content,
            file_type=file.content_type,
            skill_type=skill_type
        )
        return ExamScanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions")
async def list_questions(
    skill_type: str = None,
    error_type: str = None
):
    """获取错题列表"""
    from app.database import get_db, dict_from_row
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT * FROM questions WHERE question_type = 'error'"
    params = []

    if skill_type:
        query += " AND skill_type = ?"
        params.append(skill_type)

    if error_type:
        query += " AND error_type = ?"
        params.append(error_type)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    questions = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return {"questions": questions}

@router.get("/questions/{question_id}")
async def get_question(question_id: str):
    """获取错题详情"""
    from app.database import get_db, dict_from_row
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="错题不存在")

    return dict_from_row(row)
