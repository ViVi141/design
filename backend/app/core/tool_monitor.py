"""
工具调用监控和性能统计
"""
import time
from typing import Dict, Callable, Any
from datetime import datetime
import asyncio


class ToolMonitor:
    """工具调用监控器"""
    
    def __init__(self):
        self.stats = {
            'total_calls': 0,
            'success_calls': 0,
            'failed_calls': 0,
            'total_duration': 0.0,
            'tool_stats': {}  # 每个工具的统计
        }
    
    async def call_with_monitor(
        self, 
        tool_name: str, 
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        监控工具调用
        
        Args:
            tool_name: 工具名称
            func: 要调用的异步函数
            *args, **kwargs: 函数参数
            
        Returns:
            函数执行结果
        """
        start_time = time.time()
        
        # 初始化工具统计
        if tool_name not in self.stats['tool_stats']:
            self.stats['tool_stats'][tool_name] = {
                'calls': 0,
                'success': 0,
                'failed': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'last_call': None
            }
        
        tool_stat = self.stats['tool_stats'][tool_name]
        
        try:
            # 执行工具
            result = await func(*args, **kwargs)
            
            # 成功统计
            self.stats['success_calls'] += 1
            tool_stat['success'] += 1
            
            duration = time.time() - start_time
            self.stats['total_duration'] += duration
            tool_stat['total_duration'] += duration
            
            print(f"[监控] ✅ {tool_name} 执行成功，耗时: {duration:.2f}秒")
            
            return result
            
        except Exception as e:
            # 失败统计
            self.stats['failed_calls'] += 1
            tool_stat['failed'] += 1
            
            duration = time.time() - start_time
            self.stats['total_duration'] += duration
            tool_stat['total_duration'] += duration
            
            print(f"[监控] ❌ {tool_name} 执行失败，耗时: {duration:.2f}秒，错误: {e}")
            
            raise
            
        finally:
            # 更新统计
            self.stats['total_calls'] += 1
            tool_stat['calls'] += 1
            tool_stat['last_call'] = datetime.now().isoformat()
            
            # 更新平均耗时
            if tool_stat['calls'] > 0:
                tool_stat['avg_duration'] = tool_stat['total_duration'] / tool_stat['calls']
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = dict(self.stats)
        
        # 计算总体平均耗时
        if stats['total_calls'] > 0:
            stats['avg_duration'] = stats['total_duration'] / stats['total_calls']
        else:
            stats['avg_duration'] = 0.0
        
        # 计算成功率
        if stats['total_calls'] > 0:
            stats['success_rate'] = f"{(stats['success_calls'] / stats['total_calls'] * 100):.1f}%"
        else:
            stats['success_rate'] = "0%"
        
        return stats
    
    def get_tool_ranking(self) -> list:
        """获取工具调用排名"""
        ranking = []
        for tool_name, tool_stat in self.stats['tool_stats'].items():
            ranking.append({
                'tool': tool_name,
                'calls': tool_stat['calls'],
                'success_rate': f"{(tool_stat['success'] / tool_stat['calls'] * 100):.1f}%" if tool_stat['calls'] > 0 else "0%",
                'avg_duration': f"{tool_stat['avg_duration']:.2f}秒"
            })
        
        # 按调用次数排序
        ranking.sort(key=lambda x: x['calls'], reverse=True)
        return ranking
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_calls': 0,
            'success_calls': 0,
            'failed_calls': 0,
            'total_duration': 0.0,
            'tool_stats': {}
        }
        print("[监控] 统计已重置")


# 全局监控实例
_monitor_instance = None

def get_monitor() -> ToolMonitor:
    """获取监控器单例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ToolMonitor()
    return _monitor_instance

