"""
初始化数据库脚本
"""
import sys
import os

# 设置UTF-8编码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 添加backend目录到Python路径
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# 切换到backend目录（用于SQLite相对路径）
os.chdir(backend_path)

from app.core.database import engine, Base
from app.models import Trip, Attraction

def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("数据库初始化完成!")
    print(f"数据库位置: {engine.url}")

if __name__ == "__main__":
    init_database()

