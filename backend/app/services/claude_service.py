"""
Claude API服务
负责: 与Claude API交互，完成章节分解、笔记生成、错题分析等AI任务
"""
import os
import json
from typing import List, Dict, Any
from anthropic import Anthropic

# 初始化Anthropic客户端
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))


class ClaudeService:
    """Claude API服务类"""

    def __init__(self):
        self.client = anthropic
        self.model = "claude-sonnet-4-20250514"

    async def generate_video_notes(
        self,
        transcript_segments: List[Dict[str, Any]],
        skill_type: str,
        video_url: str
    ) -> Dict[str, Any]:
        """
        根据视频转录文本生成章节笔记

        Args:
            transcript_segments: Whisper识别的文本分段 [{"start": 0.0, "end": 5.5, "text": "..."}]
            skill_type: "adv_math" 或 "ce"
            video_url: 原始视频链接

        Returns:
            {"markdown": "...", "chapters": [...], "exercises": [...], "title": "..."}
        """
        # 合并转录文本
        full_text = "\n".join([
            f"[{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}"
            for seg in transcript_segments
        ])

        # 根据科目选择系统提示
        if skill_type == "adv_math":
            system_prompt = """你是一位经验丰富的高等数学教授。你的职责是分析课堂录音转录文本，生成结构化的学习笔记。

特点：
- 精通数学符号和公式渲染（使用LaTeX格式）
- 善于识别和标注重要的定义、定理、公式
- 能够按逻辑顺序组织章节内容
- 识别常见的数学概念混淆点并特别标注

输出格式为JSON，包含：
- title: 笔记标题
- markdown: Markdown格式的完整笔记（使用LaTeX公式）
- chapters: 章节列表，每个包含标题、时间范围、内容摘要
- exercises: 3-5道配套练习题（选择/计算/证明）
"""
        else:  # ce
            system_prompt = """你是一位经验丰富的大学英语教师。你的职责是分析英语课程录音转录文本，生成结构化的学习笔记。

特点：
- 善于提取核心词汇和短语
- 分析长难句结构
- 识别重要的语法点
- 能够按话题或技能组织章节内容

输出格式为JSON，包含：
- title: 笔记标题
- markdown: Markdown格式的完整笔记
- chapters: 章节列表，每个包含标题、时间范围、内容摘要
- exercises: 3-5道配套练习题（阅读/词汇/翻译）
"""

        # 构建用户消息
        user_message = f"""请分析以下课程录音转录文本，生成学习笔记：

视频URL: {video_url}

转录文本：
{full_text}

请按要求生成结构化的笔记内容。"""

        # 调用Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # 解析响应
        response_text = response.content[0].text

        # 尝试提取JSON
        try:
            # 尝试从响应中提取JSON部分
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            result = json.loads(json_str.strip())

            # 确保必要字段存在
            return {
                "title": result.get("title", "课程笔记"),
                "markdown": result.get("markdown", ""),
                "chapters": result.get("chapters", []),
                "exercises": result.get("exercises", [])
            }

        except json.JSONDecodeError:
            # 如果JSON解析失败，返回纯文本
            return {
                "title": "课程笔记",
                "markdown": response_text,
                "chapters": [],
                "exercises": []
            }

    async def analyze_error(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        skill_type: str
    ) -> Dict[str, Any]:
        """
        分析错题原因

        Args:
            question: 题目
            correct_answer: 正确答案
            student_answer: 学生答案
            skill_type: "adv_math" 或 "ce"

        Returns:
            {"error_type": "...", "reason": "...", "knowledge_points": [...], "related_questions": [...]}
        """
        if skill_type == "adv_math":
            error_types = "计算失误、概念混淆、思路错误、审题不清"
        else:
            error_types = "词汇不足、语法薄弱、阅读障碍、审题不清"

        system_prompt = f"""你是一位专业的学习分析师。你的职责是分析学生的错题，找出错误原因，并关联相关知识点。

错题归因类型（{skill_type}）：
- {error_types}

请以JSON格式输出分析结果，包含：
- error_type: 错误类型
- reason: 详细错误原因分析
- knowledge_points: 相关知识点列表
- related_questions: 可能相关的其他错题ID（留空列表）
"""

        user_message = f"""请分析以下错题：

题目：{question}
正确答案：{correct_answer}
学生答案：{student_answer}

请输出JSON格式的分析结果。"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            else:
                json_str = response_text
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {
                "error_type": "unknown",
                "reason": response_text,
                "knowledge_points": [],
                "related_questions": []
            }

    async def generate_exercises(
        self,
        chapter_content: str,
        skill_type: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        根据章节内容生成练习题

        Args:
            chapter_content: 章节内容
            skill_type: "adv_math" 或 "ce"
            count: 练习题数量

        Returns:
            [{"type": "...", "question": "...", "answer": "...", "explanation": "...", "difficulty": 1-5}]
        """
        if skill_type == "adv_math":
            system_prompt = """你是一位高等数学教师。你的职责是根据课程内容生成配套练习题。

题型要求：
- 选择题：考查基本概念和计算
- 填空题：考查公式和定义
- 计算题：考查解题能力
- 证明题：考查逻辑推理（可选）

难度等级：
- 1-2: 基础题
- 3-4: 中等难度
- 5: 拓展/竞赛题

请生成3-5道练习题，难度递进。输出JSON格式数组。"""
        else:
            system_prompt = """你是一位大学英语教师。你的职责是根据课程内容生成配套练习题。

题型要求：
- 阅读理解题
- 词汇/完形填空题
- 翻译题
- 语法分析题

难度等级：
- 1-2: 四级难度
- 3-4: 六级难度
- 5: 雅思/托福难度

请生成3-5道练习题，难度递进。输出JSON格式数组。"""

        user_message = f"""请根据以下章节内容生成练习题：

{chapter_content}

请生成{count}道练习题，输出JSON格式数组。"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            else:
                json_str = response_text
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return []
