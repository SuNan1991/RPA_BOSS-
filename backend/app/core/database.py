"""
MongoDB 数据库连接
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings

class Database:
    """数据库连接类"""

    client: Optional[AsyncIOMotorClient] = None

    def connect(self):
        """连接数据库"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print(f"Connected to MongoDB: {settings.MONGODB_URL}")

    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_db(self):
        """获取数据库实例"""
        return self.client[settings.DATABASE_NAME]


# 全局数据库实例
db = Database()


async def get_database():
    """获取数据库依赖注入"""
    return db.get_db()
