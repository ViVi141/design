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
    
    # 调试模式细粒度控制
    DEBUG_AGENT: bool = False          # Agent执行详细日志
    DEBUG_POI: bool = False            # POI搜索详细日志
    DEBUG_ROUTE: bool = False          # 路线规划详细日志
    DEBUG_WEATHER: bool = False        # 天气API详细日志
    DEBUG_TOOLS: bool = True           # 工具调用日志（推荐开启）
    
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
    
    # AI参数优化配置
    AI_TEMPERATURE_CREATIVE: float = 0.8  # 创意性任务（生成攻略、推荐）
    AI_TEMPERATURE_BALANCED: float = 0.7  # 平衡性任务（对话）
    AI_TEMPERATURE_PRECISE: float = 0.3   # 精确性任务（提取需求、验证）
    AI_MAX_TOKENS: int = 4000             # 最大输出token数
    AI_TIMEOUT: int = 120                 # API超时时间（秒）
    AI_STREAM_TIMEOUT: int = 180          # 流式API超时时间（秒）
    AI_MAX_RETRIES: int = 3               # 最大重试次数
    AI_RETRY_DELAY: float = 1.0           # 重试延迟（秒）
    AI_CACHE_TTL: int = 3600              # 缓存过期时间（秒）
    AI_ENABLE_CACHE: bool = True          # 是否启用缓存
    
    # 路径优化配置
    MAX_ATTRACTIONS: int = 12  # 最大景点数量
    TSP_TIME_LIMIT: int = 10  # TSP求解时间限制（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外字段


# 创建全局配置实例
settings = Settings()

