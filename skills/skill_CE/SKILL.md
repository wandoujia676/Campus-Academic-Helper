# skill_CE - 大学英语学习助手

## 描述
当用户需要分析英语课程内容并生成笔记、处理英语试卷、分析错题或生成练习题时激活此Skill。

## 触发场景
- 用户粘贴英语课程视频链接请求生成笔记
- 用户上传英语试卷图片请求分析错题
- 用户请求生成某一知识点的练习题
- 用户询问英语语法、词汇或阅读理解

## 核心能力

### 1. 阅读理解笔记
**输入**: 文章或视频转录文本
**处理**: 分析文章结构、提取核心词汇、生成概要
**输出**: 结构化笔记 + 词汇表 + 练习题

### 2. 词汇提取
- 高频词汇标注
- 词根词缀分析
- 同义词扩展
- 例句配套

### 3. 语法分析
- 句型结构分析
- 时态语态识别
- 从句类型判断
- 固定搭配总结

## 错误归因分析

### 四类归因

| 类型 | 描述 | 典型示例 |
|------|------|----------|
| **词汇不足** | 单词不认识或理解偏差 | 四级词汇不认识、熟词僻义 |
| **语法薄弱** | 句子结构分析错误 | 从句识别错误、时态混淆 |
| **阅读障碍** | 理解文章主旨困难 | 推断题答错、理解偏差 |
| **审题不清** | 题型理解有误 | 选标题题、主旨题混淆 |

## Prompt Templates

### 阅读笔记生成
```
分析以下英语文章，生成学习笔记：

文章：{article}

要求：
1. 总结文章大意（英文）
2. 提取核心词汇（附音标和例句）
3. 分析长难句结构
4. 生成理解练习题
```

### 错题分析
```
分析以下英语试卷错题：

题目：{question}
原文：{passage}
正确答案：{correct_answer}
学生答案：{student_answer}

输出：
{
  "error_type": "vocabulary|grammar|reading|comprehension",
  "reason": "错误原因",
  "knowledge_points": ["词汇/语法点列表"],
  "passage_summary": "原文要点"
}
```

## 使用限制
- 单次文章最长5000词
- 词汇提取最多100个
- 练习题每次最多5道
- 仅支持大学英语四六级难度

## 输出格式

### Markdown笔记
```markdown
# Unit X Title

## Passage Overview
- Main idea: ...
- Structure: ...

## Key Vocabulary
| 单词 | 音标 | 释义 | 例句 |
|------|------|------|------|
| word | /wɜːd/ | 含义 | 例句 |

## Sentence Analysis
**原句**: The sentence...
**结构**: 主语 + 谓语 + 宾语...
**翻译**: ...

## Practice Questions
1. [Reading] Question...
```

### JSON元数据
```json
{
  "skill_type": "ce",
  "title": "Unit X Title",
  "vocabulary": [
    {
      "word": "example",
      "phonetic": "/ɪɡˈzæmpəl/",
      "meaning": "例子",
      "example": "This is an example."
    }
  ],
  "grammar_points": [],
  "exercises": []
}
```
