import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Dental Consultation Supervisor Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Aliyun OSS & DashScope
    DASHSCOPE_API_KEY: str
    OSS_ACCESS_KEY_ID: str
    OSS_ACCESS_KEY_SECRET: str
    OSS_ENDPOINT: str = "http://oss-cn-shenzhen.aliyuncs.com"
    OSS_BUCKET_NAME: str

    # Paths
    DB_PATH: str = "data/db/dental_consultation_db.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 单例模式导出
settings = Settings()