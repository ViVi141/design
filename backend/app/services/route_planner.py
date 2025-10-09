"""
路径规划服务：使用OR-Tools优化TSP
"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import List, Dict, Tuple
import numpy as np

from app.core.config import settings
from app.services.map_service import MapService


class RoutePlanner:
    """路径规划服务：使用OR-Tools优化TSP"""
    
    def __init__(self):
        self.map_service = MapService()
        self.max_attractions = settings.MAX_ATTRACTIONS
        self.time_limit = settings.TSP_TIME_LIMIT
    
    async def optimize_route(
        self,
        attractions: List[Dict],
        constraints: Dict = None,
        budget: float = 5000,
        days: int = 3
    ) -> Dict:
        """
        优化景点访问顺序
        
        Args:
            attractions: 景点列表
            constraints: 约束条件（预算、时间等）
            
        Returns:
            优化后的行程数据
        """
        n = len(attractions)
        
        # 策略1：景点数量≤12个，使用TSP（最优解）
        if n <= self.max_attractions:
            print(f"使用TSP算法优化 {n} 个景点")
            return await self._optimize_with_tsp(attractions, budget, days)
        
        # 策略2：景点数量过多，使用贪心算法
        else:
            print(f"景点数量 {n} 超过限制，使用贪心算法")
            return await self._optimize_with_greedy(attractions, budget, days)
    
    async def _optimize_with_tsp(
        self, 
        attractions: List[Dict],
        budget: float = 5000,
        days: int = 3
    ) -> Dict:
        """使用TSP算法优化"""
        
        # 1. 构建距离矩阵
        print("构建距离矩阵...")
        distance_matrix = await self._build_distance_matrix(attractions)
        
        # 2. 使用OR-Tools求解TSP
        print("求解TSP...")
        optimal_indices = self._solve_tsp(distance_matrix)
        
        # 3. 按优化顺序重排景点
        optimal_attractions = [attractions[i] for i in optimal_indices]
        
        # 4. 获取详细路线（考虑预算）
        print("获取详细路线...")
        budget_per_day = budget / days if days > 0 else 500
        routes = await self._get_detailed_routes(optimal_attractions, budget_per_day)
        
        # 5. 计算统计信息
        summary = self._calculate_summary(optimal_attractions, routes)
        
        # 6. 计算优化率（与原始顺序对比）
        original_distance = await self._calculate_total_distance(attractions)
        optimized_distance = summary['total_distance_km'] * 1000
        if original_distance > 0:
            summary['optimization_rate'] = (original_distance - optimized_distance) / original_distance * 100
        
        return {
            'attractions': optimal_attractions,
            'routes': routes,
            'summary': summary,
            'algorithm': 'tsp'
        }
    
    async def _optimize_with_greedy(
        self, 
        attractions: List[Dict],
        budget: float = 5000,
        days: int = 3
    ) -> Dict:
        """使用贪心算法优化"""
        
        # 贪心算法：每次选择距离最近的景点
        route = [attractions[0]]
        remaining = attractions[1:].copy()
        
        while remaining:
            current = route[-1]
            # 找到距离最近的景点
            nearest = min(
                remaining, 
                key=lambda a: self.map_service.calculate_distance(
                    (current['lng'], current['lat']),
                    (a['lng'], a['lat'])
                )
            )
            route.append(nearest)
            remaining.remove(nearest)
        
        # 获取详细路线
        budget_per_day = budget / days if days > 0 else 500
        routes = await self._get_detailed_routes(route, budget_per_day)
        
        # 计算统计信息
        summary = self._calculate_summary(route, routes)
        
        return {
            'attractions': route,
            'routes': routes,
            'summary': summary,
            'algorithm': 'greedy'
        }
    
    async def _build_distance_matrix(self, attractions: List[Dict]) -> np.ndarray:
        """
        构建距离矩阵
        
        Args:
            attractions: 景点列表
            
        Returns:
            距离矩阵（n x n）
        """
        n = len(attractions)
        matrix = np.zeros((n, n))
        
        # 提取坐标
        origins = [(a['lng'], a['lat']) for a in attractions]
        destinations = origins
        
        # 使用直线距离（步行距离计算，直线距离更合理）
        # 注意：高德距离API只支持驾车(type=1)，不支持步行(type=3)
        # 对于步行场景，使用直线距离更合理且高效
        try:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        # 使用Haversine公式计算地球表面两点直线距离
                        matrix[i][j] = self.map_service.calculate_distance(
                            origins[i], origins[j]
                        )
                    else:
                        matrix[i][j] = 0
            print(f"使用直线距离构建矩阵完成")
        except Exception as e:
            print(f"计算距离失败: {e}")
            raise
        
        return matrix
    
    def _solve_tsp(self, distance_matrix: np.ndarray) -> List[int]:
        """
        使用OR-Tools求解TSP
        
        Args:
            distance_matrix: 距离矩阵
            
        Returns:
            最优访问顺序的索引列表
        """
        n = len(distance_matrix)
        
        # 创建路由模型
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        
        # 定义距离回调
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node])
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # 设置搜索参数
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = self.time_limit
        
        # 求解
        print(f"开始求解TSP（时间限制：{self.time_limit}秒）...")
        solution = routing.SolveWithParameters(search_parameters)
        
        # 提取路径
        if solution:
            route = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            
            print(f"TSP求解完成，总距离：{solution.ObjectiveValue()} 米")
            return route
        else:
            print("TSP求解失败，返回原顺序")
            return list(range(n))
    
    async def _get_detailed_routes(
        self, 
        attractions: List[Dict], 
        budget_per_day: float = 500
    ) -> List[Dict]:
        """
        获取详细路线（每两个景点之间）
        智能选择交通方式：
        - 距离<2km：步行
        - 距离2-10km：根据预算选择（紧张→公交，宽裕→出租车）
        - 距离>10km：根据预算选择（紧张→地铁/公交，宽裕→出租车）
        
        Args:
            attractions: 排序后的景点列表
            budget_per_day: 每天预算（用于判断是否紧张）
            
        Returns:
            路线列表
        """
        routes = []
        budget_tight = budget_per_day < 300  # 预算紧张阈值
        
        for i in range(len(attractions) - 1):
            origin = (attractions[i]['lng'], attractions[i]['lat'])
            destination = (attractions[i+1]['lng'], attractions[i+1]['lat'])
            
            # 先计算直线距离，用于决策交通方式
            straight_distance = self.map_service.calculate_distance(origin, destination)
            
            # 智能决策交通方式
            mode, transport_type = self._decide_transport_mode(
                straight_distance, 
                budget_tight
            )
            
            try:
                # 调用高德API获取实际路线
                route = await self.map_service.get_route(origin, destination, mode)
                
                # 估算费用
                cost = self._estimate_transport_cost(
                    route['distance'], 
                    transport_type
                )
                
                routes.append({
                    'from_idx': i,
                    'to_idx': i + 1,
                    'from_name': attractions[i]['name'],
                    'to_name': attractions[i+1]['name'],
                    'distance': route['distance'],
                    'duration': route['duration'],
                    'mode': transport_type,  # 显示给用户的交通方式
                    'cost': cost,
                    'polyline': route.get('polyline', ''),
                    'suggestion': self._get_transport_suggestion(
                        straight_distance, 
                        transport_type,
                        budget_tight
                    )
                })
                
                print(f"  {attractions[i]['name']} → {attractions[i+1]['name']}: "
                      f"{route['distance']/1000:.1f}km, {transport_type}, ¥{cost}")
                
            except Exception as e:
                print(f"获取路线失败 {attractions[i]['name']} -> {attractions[i+1]['name']}: {e}")
                # 使用直线距离作为备用
                mode_display, _ = self._decide_transport_mode(straight_distance, budget_tight)
                cost = self._estimate_transport_cost(straight_distance, mode_display)
                
                routes.append({
                    'from_idx': i,
                    'to_idx': i + 1,
                    'from_name': attractions[i]['name'],
                    'to_name': attractions[i+1]['name'],
                    'distance': straight_distance,
                    'duration': self._estimate_duration(straight_distance, mode_display),
                    'mode': mode_display,
                    'cost': cost,
                    'polyline': '',
                    'suggestion': self._get_transport_suggestion(
                        straight_distance, 
                        mode_display,
                        budget_tight
                    )
                })
        
        return routes
    
    def _decide_transport_mode(
        self, 
        distance: float, 
        budget_tight: bool
    ) -> tuple[str, str]:
        """
        根据距离和预算决定交通方式
        
        Args:
            distance: 距离（米）
            budget_tight: 是否预算紧张
            
        Returns:
            (API模式, 显示名称) 例如: ('walking', '步行')
        """
        if distance < 2000:  # <2km
            return ('walking', '步行')
        
        elif distance < 5000:  # 2-5km
            if budget_tight:
                return ('transit', '公交')  # 高德API的公交模式
            else:
                return ('driving', '出租车')
        
        elif distance < 10000:  # 5-10km
            if budget_tight:
                return ('transit', '地铁')
            else:
                return ('driving', '出租车')
        
        else:  # >10km
            if budget_tight:
                return ('transit', '地铁/公交')
            else:
                return ('driving', '出租车/网约车')
    
    def _estimate_transport_cost(self, distance: float, mode: str) -> float:
        """
        估算交通费用
        
        Args:
            distance: 距离（米）
            mode: 交通方式
            
        Returns:
            费用（元）
        """
        km = distance / 1000
        
        if mode == '步行':
            return 0
        elif mode in ['公交', '地铁', '地铁/公交']:
            # 公共交通：2-5元
            return min(5, max(2, km * 0.5))
        elif mode in ['出租车', '出租车/网约车']:
            # 出租车：起步价13元 + 2.3元/km
            return 13 + km * 2.3
        else:
            return 5  # 默认
    
    def _estimate_duration(self, distance: float, mode: str) -> float:
        """
        估算交通时间
        
        Args:
            distance: 距离（米）
            mode: 交通方式
            
        Returns:
            时间（秒）
        """
        if mode == '步行':
            return distance / 1.2  # 步行速度1.2m/s
        elif mode in ['公交', '地铁', '地铁/公交']:
            return distance / 8.3  # 公交平均速度30km/h
        elif mode in ['出租车', '出租车/网约车']:
            return distance / 11.1  # 出租车平均速度40km/h
        else:
            return distance / 5  # 默认
    
    def _get_transport_suggestion(
        self, 
        distance: float, 
        mode: str,
        budget_tight: bool
    ) -> str:
        """
        生成交通建议
        
        Args:
            distance: 距离（米）
            mode: 交通方式
            budget_tight: 是否预算紧张
            
        Returns:
            建议文本
        """
        km = distance / 1000
        
        if mode == '步行':
            return f"距离较近（{km:.1f}km），建议步行，顺便欣赏沿途风景"
        
        elif mode in ['公交', '地铁', '地铁/公交']:
            alternatives = "如果赶时间可以打车" if not budget_tight else "经济实惠的选择"
            return f"距离{km:.1f}km，建议{mode}，{alternatives}"
        
        elif mode in ['出租车', '出租车/网约车']:
            alternatives = "预算紧张可选地铁/公交" if budget_tight else "快速便捷"
            return f"距离{km:.1f}km，建议{mode}，{alternatives}"
        
        return f"距离{km:.1f}km，建议{mode}"
    
    def _calculate_summary(self, attractions: List[Dict], routes: List[Dict]) -> Dict:
        """
        计算行程摘要
        
        Args:
            attractions: 景点列表
            routes: 路线列表
            
        Returns:
            摘要信息
        """
        total_distance = sum(r['distance'] for r in routes)
        total_duration = sum(r['duration'] for r in routes)
        
        # 计算总费用
        total_cost = 0.0
        for a in attractions:
            cost_str = a.get('cost', '0')
            # 尝试提取数字
            try:
                if isinstance(cost_str, (int, float)):
                    total_cost += float(cost_str)
                elif isinstance(cost_str, str):
                    # 提取字符串中的数字
                    import re
                    numbers = re.findall(r'\d+', cost_str)
                    if numbers:
                        total_cost += float(numbers[0])
            except:
                pass
        
        return {
            'num_attractions': len(attractions),
            'total_distance_km': round(total_distance / 1000, 2),
            'total_duration_hours': round(total_duration / 3600, 2),
            'total_cost': total_cost
        }
    
    async def _calculate_total_distance(self, attractions: List[Dict]) -> float:
        """计算按原始顺序的总距离"""
        routes = await self._get_detailed_routes(attractions)
        return sum(r['distance'] for r in routes)

