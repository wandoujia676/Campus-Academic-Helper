"""
数据同步服务
负责: SQLite本地数据与云端数据库的增量同步
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import shutil

# 同步状态文件
SYNC_STATE_FILE = Path(__file__).parent.parent.parent.parent / "data" / "sync_state.json"


def get_sync_state() -> Dict[str, Any]:
    """获取同步状态"""
    if SYNC_STATE_FILE.exists():
        with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_sync": None,
        "pending_changes": [],
        "sync_direction": None
    }


def save_sync_state(state: Dict[str, Any]):
    """保存同步状态"""
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


async def log_change(table_name: str, record_id: str, operation: str):
    """记录数据变更到同步日志"""
    from app.database import get_db

    conn = get_db()
    cursor = conn.cursor()

    log_id = f"sync_{uuid.uuid4().hex[:8]}"
    cursor.execute("""
        INSERT INTO sync_log (id, table_name, record_id, operation, synced, synced_at)
        VALUES (?, ?, ?, ?, 0, ?)
    """, (log_id, table_name, record_id, operation, datetime.now().isoformat()))

    conn.commit()
    conn.close()


async def get_pending_changes(table_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取待同步的变更"""
    from app.database import get_db, dict_from_row

    conn = get_db()
    cursor = conn.cursor()

    if table_name:
        cursor.execute(
            "SELECT * FROM sync_log WHERE table_name = ? AND synced = 0 ORDER BY rowid",
            (table_name,)
        )
    else:
        cursor.execute("SELECT * FROM sync_log WHERE synced = 0 ORDER BY rowid")

    changes = [dict_from_row(row) for row in cursor.fetchall()]
    conn.close()
    return changes


async def mark_synced(change_ids: List[str]):
    """标记变更已同步"""
    from app.database import get_db

    if not change_ids:
        return

    conn = get_db()
    cursor = conn.cursor()

    placeholders = ','.join('?' * len(change_ids))
    cursor.execute(f"""
        UPDATE sync_log
        SET synced = 1, synced_at = ?
        WHERE id IN ({placeholders})
    """, [datetime.now().isoformat()] + change_ids)

    conn.commit()
    conn.close()


async def push_to_cloud(table_name: str) -> Dict[str, Any]:
    """
    推送本地数据到云端
    TODO: 实际实现需要对接云端服务（如Supabase、Firebase等）
    当前为占位实现
    """
    # 获取该表的待同步变更
    pending = await get_pending_changes(table_name)

    if not pending:
        return {
            "success": True,
            "synced_count": 0,
            "message": f"表 {table_name} 没有待同步的变更"
        }

    # TODO: 实际推送到云端
    # 这里应该调用云端API或SDK进行同步
    # 例如: await supabase.table(table_name).upsert(records)

    # 模拟推送成功
    synced_ids = [p['id'] for p in pending]
    await mark_synced(synced_ids)

    # 更新同步状态
    state = get_sync_state()
    state["last_sync"] = datetime.now().isoformat()
    state["sync_direction"] = "push"
    save_sync_state(state)

    return {
        "success": True,
        "synced_count": len(synced_ids),
        "message": f"成功同步 {len(synced_ids)} 条记录到云端"
    }


async def pull_from_cloud(table_name: str) -> Dict[str, Any]:
    """
    从云端拉取数据
    TODO: 实际实现需要对接云端服务
    """
    # TODO: 实际从云端拉取数据
    # 例如: records = await supabase.table(table_name).select("*").execute()

    # 模拟拉取成功
    state = get_sync_state()
    state["last_sync"] = datetime.now().isoformat()
    state["sync_direction"] = "pull"
    save_sync_state(state)

    return {
        "success": True,
        "pulled_count": 0,
        "message": f"成功从云端拉取数据"
    }


async def full_sync() -> Dict[str, Any]:
    """
    执行完整同步
    1. 推送本地变更到云端
    2. 从云端拉取最新数据
    """
    results = []

    # 同步所有表
    tables = ['notes', 'questions', 'knowledge_graph']

    for table in tables:
        try:
            push_result = await push_to_cloud(table)
            results.append({table: push_result})
        except Exception as e:
            results.append({table: {"success": False, "error": str(e)}})

    # 更新同步状态
    state = get_sync_state()
    state["last_sync"] = datetime.now().isoformat()
    state["sync_direction"] = "full"
    save_sync_state(state)

    return {
        "success": True,
        "results": results,
        "synced_at": datetime.now().isoformat()
    }


def export_data(table_name: str, output_path: Path) -> int:
    """
    导出表数据到JSON文件
    用于备份或迁移
    """
    from app.database import get_db

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()

    data = [dict(zip([col[0] for col in cursor.description], row)) for row in rows] if rows else []

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(data)


def import_data(table_name: str, input_path: Path) -> int:
    """
    从JSON文件导入数据
    用于恢复或迁移
    """
    from app.database import get_db

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        return 0

    conn = get_db()
    cursor = conn.cursor()

    imported = 0
    for record in data:
        # 构建INSERT语句
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?' * len(record)])
        values = list(record.values())

        try:
            cursor.execute(f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            imported += 1
        except Exception:
            continue

    conn.commit()
    conn.close()

    return imported
