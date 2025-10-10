"""
性能监控和缓存工具
⚠️ 遗留代码：主要用于旧版AI服务和性能监控API

当前使用此文件的服务：
- /api/v1/performance - 性能监控API ✅
- /api/v1/chat - 旧版AI对话（已被Agent替代）

新版Agent服务（agent_service.py）已实现更完善的重试机制，不再使用此文件的重试功能。
"""
import time
from typing import Dict, Any, Optional, List

from app.core.config import settings


class AICache:
    """简单的内存缓存实现"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not settings.AI_ENABLE_CACHE:
            return None
        
        if key in self._cache:
            item = self._cache[key]
            # 检查是否过期
            if time.time() - item['timestamp'] < settings.AI_CACHE_TTL:
                print(f"[缓存命中] {key[:50]}...")
                return item['value']
            else:
                # 过期，删除
                del self._cache[key]
        
        return None
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        if not settings.AI_ENABLE_CACHE:
            return
        
        self._cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        
        # 简单的LRU：缓存超过1000项时清理旧的
        if len(self._cache) > 1000:
            # 删除最旧的100项
            sorted_items = sorted(
                self._cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            for key, _ in sorted_items[:100]:
                del self._cache[key]
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
_ai_cache = AICache()


def get_cache() -> AICache:
    """获取缓存实例"""
    return _ai_cache


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def record(self, operation: str, duration: float, success: bool, **kwargs):
        """记录性能数据"""
        self.metrics.append({
            'operation': operation,
            'duration': duration,
            'success': success,
            'timestamp': time.time(),
            **kwargs
        })
        
        # 只保留最近100条
        if len(self.metrics) > 100:
            self.metrics = self.metrics[-100:]
        
        # 打印性能日志
        status = "✓" if success else "✗"
        print(f"[性能] {status} {operation}: {duration:.2f}秒")
    
    def get_stats(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """获取统计数据"""
        if operation:
            filtered = [m for m in self.metrics if m['operation'] == operation]
        else:
            filtered = self.metrics
        
        if not filtered:
            return {}
        
        durations = [m['duration'] for m in filtered]
        success_count = sum(1 for m in filtered if m['success'])
        
        return {
            'total_calls': len(filtered),
            'success_rate': success_count / len(filtered) * 100,
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations)
        }


# 全局性能监控器
_performance_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """获取性能监控器"""
    return _performance_monitor


# ==================== 以下为遗留代码 ====================
# ⚠️ 注意：
# - retry_with_backoff: 已被 agent_service.py 中的 _retry_tool_call 替代
# - OptimizedAIBase: 仅用于旧版 ai_service.py，建议迁移到Agent
# ======================================================

# 保留此函数仅用于向后兼容
async def retry_with_backoff(
    func,
    max_retries: int = None,
    initial_delay: float = None,
    backoff_factor: float = 2.0
):
    """
    带指数退避的重试装饰器（遗留函数，建议使用agent_service.py中的实现）
    
    Args:
        func: 要执行的异步函数
        max_retries: 最大重试次数
        initial_delay: 初始延迟
        backoff_factor: 退避因子
    """
    import asyncio
    max_retries = max_retries or settings.AI_MAX_RETRIES
    initial_delay = initial_delay or settings.AI_RETRY_DELAY
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries:
                delay = initial_delay * (backoff_factor ** attempt)
                if settings.DEBUG:
                    print(f"[重试-旧版] 第{attempt + 1}次失败，{delay:.1f}秒后重试: {str(e)[:100]}")
                await asyncio.sleep(delay)
            else:
                if settings.DEBUG:
                    print(f"[重试-旧版] 达到最大重试次数({max_retries})，放弃")
    
    raise last_exception


class OptimizedAIBase:
    """
    优化的AI服务基类（遗留类，仅用于旧版ai_service.py）
    
    ⚠️ 新项目请使用 agent_service.py 中的 TravelPlannerAgent
    """
    
    def __init__(self):
        self.cache = get_cache()
        self.monitor = get_monitor()
    
    def create_llm(
        self,
        temperature: float = None,
        max_tokens: int = None,
        streaming: bool = False,
        **kwargs
    ):
        """
        创建LLM实例（遗留方法）
        
        Args:
            temperature: 温度参数
            max_tokens: 最大token数
            streaming: 是否启用流式输出
            **kwargs: 其他参数
        """
        from langchain_openai import ChatOpenAI
        
        temperature = temperature if temperature is not None else settings.AI_TEMPERATURE_BALANCED
        max_tokens = max_tokens if max_tokens is not None else settings.AI_MAX_TOKENS
        timeout = settings.AI_STREAM_TIMEOUT if streaming else settings.AI_TIMEOUT
        
        return ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_API_BASE,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            streaming=streaming,
            **kwargs
        )
    
    def generate_cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        import hashlib
        import json
        # 将参数序列化为字符串
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        
        # 生成MD5哈希
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def call_with_cache_and_retry(
        self,
        operation: str,
        func,
        cache_key: Optional[str] = None,
        enable_cache: bool = True
    ):
        """
        带缓存和重试的AI调用（遗留方法）
        
        Args:
            operation: 操作名称（用于监控）
            func: 要执行的异步函数
            cache_key: 缓存键
            enable_cache: 是否启用缓存
        """
        start_time = time.time()
        
        # 尝试从缓存获取
        if enable_cache and cache_key:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                duration = time.time() - start_time
                self.monitor.record(
                    operation=operation,
                    duration=duration,
                    success=True,
                    cached=True
                )
                return cached_result
        
        # 执行函数（带重试）
        try:
            result = await retry_with_backoff(func)
            
            # 缓存结果
            if enable_cache and cache_key:
                self.cache.set(cache_key, result)
            
            # 记录性能
            duration = time.time() - start_time
            self.monitor.record(
                operation=operation,
                duration=duration,
                success=True,
                cached=False
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.monitor.record(
                operation=operation,
                duration=duration,
                success=False,
                error=str(e)[:100]
            )
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.monitor.get_stats()


# ==================== 整合说明 ====================
# 
# 此文件已整合优化（2025-10-10）：
#
# ✅ 保留部分：
# - AICache：缓存工具（性能监控API使用）
# - PerformanceMonitor：性能监控（/api/v1/performance使用）
# 
# ⚠️ 遗留部分（向后兼容）：
# - retry_with_backoff：旧版重试函数
# - OptimizedAIBase：旧版基类（仅ai_service.py使用）
#
# 🎯 推荐迁移路径：
# - 新功能 → agent_service.py（TravelPlannerAgent）
# - 旧AI对话 → 考虑迁移到Agent或保持现状
# - 性能监控 → 继续使用此文件的monitor和cache
#
# ==================================================
