# 大学助手 1.0

AI驱动的学习辅助系统，为大学生打造。

## 核心功能

### 📹 视频笔记
- 支持B站、YouTube等视频链接
- AI自动章节分解
- 生成结构化Markdown笔记
- 配套练习题生成

### 📄 试卷扫描
- 图片OCR识别
- 错题自动提取
- AI归因分析（计算失误/概念混淆/思路错误/审题不清）
- 知识点关联

### 📚 错题本
- 持久化存储
- 按知识点分类
- 复习进度追踪

## 技术栈

- **前端**: React 18 + TypeScript + Vite
- **后端**: FastAPI (Python)
- **数据库**: SQLite
- **AI**: Claude API + Whisper + PaddleOCR

## 快速开始

### 1. 安装依赖

```bash
# 前端
cd frontend
npm install

# 后端
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 终端1: 启动后端
cd backend
uvicorn main:app --reload --port 8000

# 终端2: 启动前端
cd frontend
npm run dev
```

### 3. 访问应用

打开浏览器访问: http://localhost:5173

## 项目文档

- [产品需求文档](../Prd.md)
- [开发规范](CLAUDE.md)

## 版本历史

- **1.0** - 初始版本，包含视频笔记、试卷扫描、错题本核心功能

## License

ISC
