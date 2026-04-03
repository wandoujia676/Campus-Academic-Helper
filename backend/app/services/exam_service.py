"""
试卷扫描服务
负责: 图片预处理 -> OCR识别 -> 错题提取 -> AI归因分析 -> 存储
"""
import uuid
import json
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.services.claude_service import ClaudeService
from fastapi import HTTPException

claude_service = ClaudeService()


async def process_exam(
    file_content: bytes,
    file_type: str,
    skill_type: str
) -> dict:
    """
    处理试卷图片并提取错题
    完整流程:
    1. 图片预处理 (resize, 去噪, 二值化)
    2. OCR识别 (PaddleOCR)
    3. 文本结构化 (题目与答案分离)
    4. AI错题归因分析 (Claude)
    5. 知识点关联
    6. 存储到数据库
    """
    note_id = f"note_{uuid.uuid4().hex[:8]}"

    # 创建临时文件
    temp_dir = Path(tempfile.mkdtemp())
    image_path = temp_dir / f"exam_{uuid.uuid4().hex[:8]}.jpg"

    try:
        # 保存上传的图片
        with open(image_path, 'wb') as f:
            f.write(file_content)

        # Step 1: OCR识别
        ocr_text = await ocr_recognize(image_path)

        if not ocr_text:
            raise HTTPException(status_code=400, detail="未能识别到试卷内容，请确保图片清晰")

        # Step 2: AI分析错题
        skill_name = "adv_math" if skill_type == "adv_math" else "ce"
        result = await claude_service.analyze_exam_paper(
            ocr_text=ocr_text,
            skill_type=skill_name
        )

        questions = result.get("questions", [])
        summary = result.get("summary", {"totalErrors": 0, "byType": {}})

        # 保存错题到数据库
        await save_questions(
            questions=questions,
            skill_type=skill_type,
            note_id=note_id
        )

        return {
            "id": note_id,
            "status": "completed",
            "questions": questions,
            "summary": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"试卷扫描失败: {str(e)}")

    finally:
        # 清理临时文件
        try:
            if image_path.exists():
                image_path.unlink()
            temp_dir.rmdir()
        except:
            pass


async def preprocess_image(image_content: bytes) -> bytes:
    """
    图片预处理
    - 调整大小
    - 去噪
    - 增强对比度
    """
    try:
        import cv2
        import numpy as np

        # 解码图片
        nparr = np.frombuffer(image_content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return image_content

        # 调整大小（如果太大）
        max_dimension = 2000
        height, width = img.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale)

        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 去噪
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 增强对比度 (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        # 转换回BGR
        result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        # 编码为JPEG
        _, buffer = cv2.imencode('.jpg', result, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return buffer.tobytes()

    except ImportError:
        # 如果没有OpenCV，返回原始图片
        return image_content


async def ocr_recognize(image_path: Path) -> Optional[str]:
    """
    使用PaddleOCR进行OCR文字识别
    返回识别的文本
    """
    try:
        from paddleocr import PaddleOCR

        # 初始化OCR（使用中文模型）
        ocr = PaddleOCR(
            lang='ch',
            use_angle_cls=True,
            show_log=False
        )

        # 执行OCR
        result = ocr.ocr(str(image_path), cls=True)

        if not result or not result[0]:
            return None

        # 提取文本
        texts = []
        for line in result[0]:
            if line and len(line) >= 2:
                text = line[1][0] if isinstance(line[1], (list, tuple)) else line[1]
                if text:
                    texts.append(text)

        return "\n".join(texts)

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PaddleOCR未安装，请运行: pip install paddleocr"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")


async def extract_questions(ocr_text: str) -> List[Dict[str, Any]]:
    """
    从OCR文本中提取题目
    使用Claude识别题目结构
    """
    # 这个功能已合并到 ClaudeService.analyze_exam_paper 中
    pass


async def save_questions(
    questions: List[Dict[str, Any]],
    skill_type: str,
    note_id: str
) -> None:
    """保存错题到数据库"""
    from app.database import get_db

    conn = get_db()
    cursor = conn.cursor()

    for q in questions:
        cursor.execute("""
            INSERT INTO questions (
                id, note_id, skill_type, question_text, answer_text,
                error_type, knowledge_points, difficulty, source,
                question_type, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            q.get("id", f"q_{uuid.uuid4().hex[:6]}"),
            note_id,
            skill_type,
            q.get("text", ""),
            q.get("answer", ""),
            q.get("error_type"),
            json.dumps(q.get("knowledge_points", []), ensure_ascii=False),
            q.get("difficulty", 1),
            q.get("source", ""),
            "error",
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()
