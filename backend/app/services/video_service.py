"""
视频处理服务
负责: URL解析 -> 视频下载 -> 语音识别 -> AI章节分解 -> 笔记生成
"""
import uuid
import json
import re
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import HTTPException

# 导入Claude服务
from app.services.claude_service import ClaudeService

# 初始化Claude服务
claude_service = ClaudeService()


def detect_platform(url: str) -> str:
    """检测视频平台"""
    if "bilibili" in url or "b23.tv" in url:
        return "bilibili"
    elif "youtube" in url:
        return "youtube"
    elif "douyin" in url:
        return "douyin"
    return "unknown"


async def process_video(url: str, skill_type: str) -> dict:
    """
    处理视频并生成笔记
    完整流程:
    1. URL解析与验证
    2. 视频下载 (yt-dlp)
    3. 音频提取 (FFmpeg)
    4. 语音识别 (Whisper)
    5. AI章节分解 (Claude)
    6. 生成Markdown笔记 + JSON元数据 + 练习题
    """
    note_id = f"note_{uuid.uuid4().hex[:8]}"
    platform = detect_platform(url)

    # 创建临时目录
    temp_dir = Path(tempfile.mkdtemp())
    video_path: Optional[Path] = None
    audio_path: Optional[Path] = None

    try:
        # Step 1: 下载视频
        video_path = await download_video(url, temp_dir, platform)

        # Step 2: 提取音频
        audio_path = await extract_audio(video_path, temp_dir)

        # Step 3: 语音识别
        transcript_segments = await transcribe_audio(audio_path)

        # Step 4: AI章节分解与笔记生成
        skill_name = "adv_math" if skill_type == "adv_math" else "ce"
        result = await claude_service.generate_video_notes(
            transcript_segments=transcript_segments,
            skill_type=skill_name,
            video_url=url
        )

        markdown_content = result["markdown"]
        chapters = result["chapters"]
        exercises = result["exercises"]
        title = result.get("title", "视频笔记")

        json_metadata = {
            "skill_type": skill_type,
            "title": title,
            "chapters": chapters,
            "duration": sum(ch.get("endTime", 0) - ch.get("startTime", 0) for ch in chapters),
            "platform": platform,
            "source_url": url,
            "generated_at": datetime.now().isoformat()
        }

        # 保存到数据库
        await save_note(
            note_id=note_id,
            skill_type=skill_type,
            title=title,
            source_type="video",
            source_url=url,
            markdown_content=markdown_content,
            json_metadata=json_metadata
        )

        return {
            "id": note_id,
            "status": "completed",
            "markdown": markdown_content,
            "metadata": json_metadata,
            "exercises": exercises
        }

    except Exception as e:
        # 如果任何步骤失败，返回错误
        raise HTTPException(status_code=500, detail=f"视频处理失败: {str(e)}")

    finally:
        # 清理临时文件
        for path in [video_path, audio_path]:
            if path and path.exists():
                try:
                    path.unlink()
                except:
                    pass
        try:
            temp_dir.rmdir()
        except:
            pass


async def download_video(url: str, temp_dir: Path, platform: str) -> Path:
    """下载视频到本地"""
    import yt_dlp

    video_path = temp_dir / f"video_{uuid.uuid4().hex[:8]}.mp4"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(video_path.with_suffix('.%(ext)s')),
        'quiet': True,
        'no_warnings': True,
    }

    # 平台特定选项
    if platform == "bilibili":
        ydl_opts['extract_audio'] = True
        ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 获取实际下载的文件路径
            if info and 'entries' in info:
                # 播放列表，取第一个
                info = info['entries'][0]
            actual_path = Path(ydl.prepare_filename(info))
            if not actual_path.exists():
                actual_path = video_path
            return actual_path
    except Exception as e:
        raise Exception(f"视频下载失败: {str(e)}")


async def extract_audio(video_path: Path, temp_dir: Path) -> Path:
    """提取音频"""
    audio_path = temp_dir / f"audio_{uuid.uuid4().hex[:8]}.wav"

    try:
        # 使用FFmpeg提取音频
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不要视频
            '-acodec', 'pcm_s16le',  # WAV格式
            '-ar', '16000',  # 16kHz采样率
            '-ac', '1',  # 单声道
            '-y',  # 覆盖输出
            str(audio_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode != 0:
            raise Exception(f"音频提取失败: {result.stderr}")

        return audio_path

    except subprocess.TimeoutExpired:
        raise Exception("音频提取超时")
    except FileNotFoundError:
        raise Exception("FFmpeg未安装，请先安装FFmpeg")


async def transcribe_audio(audio_path: Path) -> list:
    """
    使用Whisper进行语音识别
    返回格式: [{"start": 0.0, "end": 5.5, "text": "文本"}]
    """
    try:
        import whisper
    except ImportError:
        raise Exception("Whisper未安装，请运行: pip install openai-whisper")

    try:
        # 加载模型（使用base模型平衡速度和准确度）
        model = whisper.load_model("base")

        # 转录
        result = model.transcribe(
            str(audio_path),
            language="zh",  # 中文
            fp16=False,  # CPU模式
        )

        # 转换为分段格式
        segments = []
        for segment in result.get("segments", []):
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })

        if not segments:
            raise Exception("未能识别到语音内容")

        return segments

    except Exception as e:
        raise Exception(f"语音识别失败: {str(e)}")


async def save_note(
    note_id: str,
    skill_type: str,
    title: str,
    source_type: str,
    source_url: str,
    markdown_content: str,
    json_metadata: dict
):
    """保存笔记到数据库"""
    from app.database import get_db

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notes (
            id, skill_type, title, source_type, source_url,
            markdown_content, json_metadata, chapter_count,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        note_id,
        skill_type,
        title,
        source_type,
        source_url,
        markdown_content,
        json.dumps(json_metadata, ensure_ascii=False),
        len(json_metadata.get("chapters", [])),
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()
