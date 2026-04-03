import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "learnmate.db"

def get_db():
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    conn = get_db()
    cursor = conn.cursor()

    # 科目表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 章节表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            title TEXT NOT NULL,
            video_url TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        )
    """)

    # 笔记表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            chapter_id TEXT,
            skill_type TEXT NOT NULL,
            title TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_url TEXT,
            markdown_content TEXT NOT NULL,
            json_metadata TEXT,
            chapter_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_at TIMESTAMP,
            deleted INTEGER DEFAULT 0,
            FOREIGN KEY (chapter_id) REFERENCES chapters(id)
        )
    """)

    # 题目表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id TEXT PRIMARY KEY,
            note_id TEXT,
            skill_type TEXT NOT NULL,
            question_text TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            error_type TEXT,
            knowledge_points TEXT,
            difficulty INTEGER DEFAULT 1,
            source TEXT,
            question_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id)
        )
    """)

    # 知识点关联表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_graph (
            id TEXT PRIMARY KEY,
            skill_type TEXT NOT NULL,
            topic TEXT NOT NULL,
            subtopics TEXT,
            related_question_ids TEXT,
            mastery_level INTEGER DEFAULT 0,
            last_reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 同步日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
            id TEXT PRIMARY KEY,
            table_name TEXT NOT NULL,
            record_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            synced_at TIMESTAMP,
            synced INTEGER DEFAULT 0
        )
    """)

    # 插入默认科目
    cursor.execute("""
        INSERT OR IGNORE INTO subjects (id, name, code) VALUES
        ('sub_math', '高等数学', 'adv_math'),
        ('sub_ce', '大学英语', 'ce')
    """)

    conn.commit()
    conn.close()

def dict_from_row(row: sqlite3.Row) -> dict:
    """将sqlite Row转换为字典"""
    return dict(zip(row.keys(), row))
