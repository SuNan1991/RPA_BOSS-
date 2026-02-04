"""
配置文件
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "BOSS_RPA"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-this-in-production"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MongoDB配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "boss_rpa"

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "../logs"

    # RPA配置
    RPA_HEADLESS: bool = False
    RPA_TIMEOUT: int = 30000

    # BOSS直聘配置
    BOSS_URL: str = "https://www.zhipin.com"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
