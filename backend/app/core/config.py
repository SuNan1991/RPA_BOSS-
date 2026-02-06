"""
配置文件
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


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

    # SQLite配置
    SQLITE_DB_PATH: str = "data/boss_rpa.db"

    # CORS配置
    # 开发环境允许所有源，生产环境请限制具体域名
    CORS_ORIGINS: list[str] = ["*"]  # 开发模式允许所有源

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


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
