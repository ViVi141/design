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
        constraints: Dict = None
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
            return await self._optimize_with_tsp(attractions)
        
        # 策略2：景点数量过多，使用贪心算法
        else:
            print(f"景点数量 {n} 超过限制，使用贪心算法")
            return await self._optimize_with_greedy(attractions)
    
    async def _optimize_with_tsp(self, attractions: List[Dict]) -> Dict:
        """使用TSP算法优化"""
        
        # 1. 构建距离矩阵
        print("构建距离矩阵...")
        distance_matrix = await self._build_distance_matrix(attractions)
        
        # 2. 使用OR-Tools求解TSP
        print("求解TSP...")
        optimal_indices = self._solve_tsp(distance_matrix)
        
        # 3. 按优化顺序重排景点
        optimal_attractions = [attractions[i] for i in optimal_indices]
        
        # 4. 获取详细路线
        print("获取详细路线...")
        routes = await self._get_detailed_routes(optimal_attractions)
        
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
    
    async def _optimize_with_greedy(self, attractions: List[Dict]) -> Dict:
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
        routes = await self._get_detailed_routes(route)
        
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
        
        # 批量调用高德API获取距离
        try:
            results = await self.map_service.get_distance_matrix(
                origins, destinations, type=3  # 步行距离
            )
            
            # 填充矩阵
            for i, result_row in enumerate(results):
                for j, item in enumerate(result_row):
                    distance = float(item.get('distance', 0))
                    matrix[i][j] = distance
        except Exception as e:
            print(f"API调用失败，使用直线距离: {e}")
            # 如果API失败，使用直线距离
            for i in range(n):
                for j in range(n):
                    if i != j:
                        matrix[i][j] = self.map_service.calculate_distance(
                            origins[i], origins[j]
                        )
        
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
    
    async def _get_detailed_routes(self, attractions: List[Dict]) -> List[Dict]:
        """
        获取详细路线（每两个景点之间）
        
        Args:
            attractions: 排序后的景点列表
            
        Returns:
            路线列表
        """
        routes = []
        
        for i in range(len(attractions) - 1):
            origin = (attractions[i]['lng'], attractions[i]['lat'])
            destination = (attractions[i+1]['lng'], attractions[i+1]['lat'])
            
            try:
                # 调用高德API获取路线
                route = await self.map_service.get_route(origin, destination, 'walking')
                routes.append({
                    'from_idx': i,
                    'to_idx': i + 1,
                    'from_name': attractions[i]['name'],
                    'to_name': attractions[i+1]['name'],
                    'distance': route['distance'],
                    'duration': route['duration'],
                    'mode': 'walking',
                    'polyline': route.get('polyline', '')
                })
            except Exception as e:
                print(f"获取路线失败 {attractions[i]['name']} -> {attractions[i+1]['name']}: {e}")
                # 使用直线距离作为备用
                distance = self.map_service.calculate_distance(origin, destination)
                routes.append({
                    'from_idx': i,
                    'to_idx': i + 1,
                    'from_name': attractions[i]['name'],
                    'to_name': attractions[i+1]['name'],
                    'distance': distance,
                    'duration': distance / 1.2,  # 假设步行速度1.2m/s
                    'mode': 'walking',
                    'polyline': ''
                })
        
        return routes
    
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

