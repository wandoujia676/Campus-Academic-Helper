"""
LearnMate Backend - AI学习助手后端服务
FastAPI + SQLite
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import video, exam, sync
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时可以做清理工作


app = FastAPI(
    title="大学助手 API",
    description="大学助手 - AI学习辅助系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(video.router, prefix="/api/video", tags=["视频笔记"])
app.include_router(exam.router, prefix="/api/exam", tags=["试卷扫描"])
app.include_router(sync.router, prefix="/api/sync", tags=["数据同步"])


@app.get("/")
async def root():
    return {"message": "大学助手 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
