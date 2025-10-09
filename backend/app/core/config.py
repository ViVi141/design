"""
配置管理模块
使用 Pydantic Settings 管理环境变量
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """应用配置"""
    
    # 项目信息
    PROJECT_NAME: str = "智能旅行规划系统"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # API密钥
    AMAP_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./data/app.db"
    
    # CORS (使用逗号分隔的字符串)
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    def get_cors_origins(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    # DeepSeek API配置
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 路径优化配置
    MAX_ATTRACTIONS: int = 12  # 最大景点数量
    TSP_TIME_LIMIT: int = 10  # TSP求解时间限制（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外字段


# 创建全局配置实例
settings = Settings()

