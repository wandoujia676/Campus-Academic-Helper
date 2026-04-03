"""
LearnMate Backend - AI学习助手后端服务
FastAPI + SQLite
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import video, exam, sync
from app.database import init_db

app = FastAPI(
    title="LearnMate API",
    description="乐乐学业助手 - AI学习辅助系统后端API",
    version="1.0.0"
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

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "LearnMate API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
