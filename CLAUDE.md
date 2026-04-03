# 大学助手 1.0

AI驱动的学习辅助系统，帮助大学生建立良好的学习习惯。

## 项目结构

```
university-helper/
├── frontend/          # React + TypeScript + Vite 前端
├── backend/           # FastAPI Python 后端
│   └── app/
│       ├── router/    # API路由
│       ├── services/  # 业务逻辑
│       ├── skills/    # AI Skill定义
│       ├── models/    # 数据模型
│       └── database/  # SQLite数据库
├── skills/           # Claude Skills定义
│   ├── skill_Adv.Math/
│   └── skill_CE/
└── data/             # 数据存储
```

## 开发命令

### 前端
```bash
cd frontend
npm install
npm run dev    # 开发服务器 http://localhost:5173
npm run build  # 生产构建
```

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, TypeScript, Vite, Zustand |
| 后端 | FastAPI, Python 3.11+ |
| 数据库 | SQLite |
| AI | Claude API, Whisper, PaddleOCR |
| 视频处理 | FFmpeg, yt-dlp |

## API端点

- `POST /api/video/notes` - 生成视频笔记
- `GET /api/video/notes` - 获取笔记列表
- `POST /api/exam/scan` - 扫描试卷
- `GET /api/exam/questions` - 获取错题列表
- `POST /api/sync/push` - 推送数据到云端

## 关键规则

1. 所有API请求通过 `/api` 前缀
2. 前端代理 `localhost:5173` → `localhost:8000`
3. 数据库文件位于 `data/learnmate.db`
4. Skill定义文件位于 `skills/` 目录

## 版本号规则

- 主版本号.次版本号 (如 1.0, 1.1, 1.2...)
- 次版本号递增：新增功能或重要更新
- 主版本号递增：重大架构变更
