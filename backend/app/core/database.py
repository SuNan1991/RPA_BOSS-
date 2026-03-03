"""
SQLite 数据库连接
"""

from pathlib import Path
from typing import Optional

import aiosqlite

from .config import settings


class Database:
    """SQLite数据库连接类"""

    def __init__(self):
        self.db_path = Path(settings.SQLITE_DB_PATH)
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """连接数据库"""
        # 确保数据库目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建连接
        self._connection = await aiosqlite.connect(self.db_path)

        # 配置WAL模式以提高并发性能
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA synchronous=NORMAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")

        print(f"Connected to SQLite: {self.db_path}")

    async def close(self):
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            print("Closed SQLite connection")

    async def get_connection(self) -> aiosqlite.Connection:
        """获取数据库连接"""
        if not self._connection:
            await self.connect()
        return self._connection


# 全局数据库实例
db = Database()


async def get_database() -> aiosqlite.Connection:
    """获取数据库依赖注入"""
    return await db.get_connection()


async def init_database():
    """初始化数据库（创建schema）"""
    # 总是调用 create_schema，因为它使用 CREATE TABLE IF NOT EXISTS
    # 这样可以确保所有表都存在
    print("Ensuring database schema is up to date...")
    await create_schema()


async def create_schema():
    """创建数据库表结构"""
    conn = await db.get_connection()

    # 创建accounts表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL UNIQUE,
            username TEXT,
            is_active BOOLEAN DEFAULT 1,
            cookie_status TEXT DEFAULT 'none',
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建jobs表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            company_name TEXT NOT NULL,
            salary TEXT,
            city TEXT,
            area TEXT,
            experience TEXT,
            education TEXT,
            company_size TEXT,
            industry TEXT,
            job_url TEXT NOT NULL,
            boss_title TEXT,
            status TEXT DEFAULT 'pending',
            is_applied BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建tasks表
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            config TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建sessions表 (用于RPA会话管理)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookies BLOB NOT NULL,
            user_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)

    # 创建login_logs表 (用于登录日志)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            success BOOLEAN DEFAULT 0,
            failure_reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建索引
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_phone ON accounts(phone)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_accounts_is_active ON accounts(is_active)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_task_type ON tasks(task_type)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)")
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_login_logs_timestamp ON login_logs(timestamp)"
    )

    await conn.commit()
    print("Database schema created successfully")
