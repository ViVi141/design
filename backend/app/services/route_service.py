"""
路线规划服务 - 使用高德地图路径规划2.0（v5 API）
"""
import httpx
from typing import Dict, Optional, Tuple, List
from enum import Enum


class DrivingStrategy(Enum):
    """驾车策略"""
    SPEED_PRIORITY = 0  # 速度优先
    FEE_PRIORITY = 1  # 费用优先
    NORMAL_FAST = 2  # 常规最快
    DEFAULT = 32  # 默认推荐（高德推荐）
    AVOID_CONGESTION = 33  # 躲避拥堵
    HIGHWAY_PRIORITY = 34  # 高速优先
    NO_HIGHWAY = 35  # 不走高速
    LESS_FEE = 36  # 少收费
    MAIN_ROAD = 37  # 大路优先
    FASTEST = 38  # 速度最快


class TransitStrategy(Enum):
    """公交策略"""
    RECOMMEND = 0  # 推荐模式
    CHEAPEST = 1  # 最经济
    LEAST_TRANSFER = 2  # 最少换乘
    LEAST_WALKING = 3  # 最少步行
    COMFORTABLE = 4  # 最舒适
    NO_SUBWAY = 5  # 不乘地铁
    SUBWAY_MAP = 6  # 地铁图模式
    SUBWAY_PRIORITY = 7  # 地铁优先
    TIME_SHORT = 8  # 时间短


class RouteService:
    """路线规划服务（v5 API）"""
    
    def __init__(self):
        self.api_key = "your_key"
        self.base_url = "https://restapi.amap.com/v5"
    
    async def get_driving_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        strategy: DrivingStrategy = DrivingStrategy.DEFAULT,
        waypoints: List[Tuple[float, float]] = None,
        avoid_polygons: List[List[Tuple[float, float]]] = None,
        plate: str = None
    ) -> Optional[Dict]:
        """
        获取驾车路线（v5 API）
        
        Args:
            origin: 起点 (lng, lat)
            destination: 终点 (lng, lat)
            strategy: 驾车策略
            waypoints: 途经点列表，最多16个
            avoid_polygons: 避让区域
            plate: 车牌号（判断限行）
            
        Returns:
            {
                'distance': 总距离(米),
                'duration': 总耗时(秒),
                'tolls': 过路费(元),
                'traffic_lights': 红绿灯数量,
                'paths': 路线列表,
                'taxi_cost': 预估出租车费用
            }
        """
        url = f"{self.base_url}/direction/driving"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'strategy': strategy.value,
            'show_fields': 'cost,navi,polyline',
            'ferry': 0  # 使用轮渡
        }
        
        # 途经点
        if waypoints:
            waypoints_str = ';'.join([f"{wp[0]},{wp[1]}" for wp in waypoints])
            params['waypoints'] = waypoints_str
        
        # 避让区域
        if avoid_polygons:
            polygons_str = '|'.join([
                ','.join([f"{p[0]},{p[1]}" for p in polygon])
                for polygon in avoid_polygons
            ])
            params['avoidpolygons'] = polygons_str
        
        # 车牌号
        if plate:
            params['plate'] = plate
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route', {})
                paths = route.get('paths', [])
                
                if paths:
                    path = paths[0]
                    cost = path.get('cost', {})
                    
                    return {
                        'origin': route.get('origin'),
                        'destination': route.get('destination'),
                        'taxi_cost': route.get('taxi_cost'),
                        'distance': int(path.get('distance', 0)),
                        'duration': int(cost.get('duration', 0)),
                        'tolls': float(cost.get('tolls', 0)),
                        'toll_distance': int(cost.get('toll_distance', 0)),
                        'traffic_lights': int(cost.get('traffic_lights', 0)),
                        'restriction': path.get('restriction', 0),
                        'paths': paths,
                        'polyline': path.get('polyline', '')
                    }
            else:
                print(f"[驾车规划] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[驾车规划] 异常: {e}")
            return None
    
    async def get_walking_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        is_indoor: bool = False
    ) -> Optional[Dict]:
        """
        获取步行路线（v5 API）
        
        Args:
            origin: 起点 (lng, lat)
            destination: 终点 (lng, lat)
            is_indoor: 是否室内算路
            
        Returns:
            {
                'distance': 总距离(米),
                'duration': 总耗时(秒),
                'paths': 路线列表
            }
        """
        url = f"{self.base_url}/direction/walking"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'isindoor': 1 if is_indoor else 0,
            'show_fields': 'cost,polyline'
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route', {})
                paths = route.get('paths', [])
                
                if paths:
                    path = paths[0]
                    cost = path.get('cost', {})
                    
                    return {
                        'origin': route.get('origin'),
                        'destination': route.get('destination'),
                        'distance': int(path.get('distance', 0)),
                        'duration': int(cost.get('duration', 0)),
                        'paths': paths,
                        'polyline': path.get('polyline', '')
                    }
            else:
                print(f"[步行规划] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[步行规划] 异常: {e}")
            return None
    
    async def get_transit_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        city1: str = "010",
        city2: str = "010",
        strategy: TransitStrategy = TransitStrategy.RECOMMEND,
        alternative_route: int = 3
    ) -> Optional[Dict]:
        """
        获取公交路线（v5 API）
        
        Args:
            origin: 起点 (lng, lat)
            destination: 终点 (lng, lat)
            city1: 起点城市citycode
            city2: 终点城市citycode
            strategy: 公交策略
            alternative_route: 返回方案数(1-10)
            
        Returns:
            {
                'transits': 公交方案列表,
                'count': 方案数量
            }
        """
        url = f"{self.base_url}/direction/transit/integrated"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'city1': city1,
            'city2': city2,
            'strategy': strategy.value,
            'AlternativeRoute': alternative_route,
            'show_fields': 'cost,polyline'
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route', {})
                transits = route.get('transits', [])
                
                # 提取换乘方案信息
                plans = []
                for transit in transits:
                    cost = transit.get('cost', {})
                    segments = transit.get('segments', [])
                    
                    # 提取线路信息
                    lines = []
                    for seg in segments:
                        if seg.get('bus'):
                            bus = seg['bus']
                            buslines = bus.get('buslines', [])
                            for line in buslines:
                                lines.append({
                                    'name': line.get('name'),
                                    'type': line.get('type'),
                                    'via_num': line.get('via_num', 0)
                                })
                    
                    # 安全转换（处理空字符串）
                    def safe_int(value, default=0):
                        try:
                            return int(value) if value and str(value).strip() else default
                        except (ValueError, TypeError):
                            return default
                    
                    def safe_float(value, default=0.0):
                        try:
                            return float(value) if value and str(value).strip() else default
                        except (ValueError, TypeError):
                            return default
                    
                    plans.append({
                        'distance': safe_int(transit.get('distance'), 0),
                        'duration': safe_int(cost.get('duration'), 0),
                        'transit_fee': safe_float(cost.get('transit_fee'), 0),
                        'taxi_fee': safe_float(cost.get('taxi_fee'), 0),
                        'walking_distance': safe_int(transit.get('walking_distance'), 0),
                        'lines': lines,
                        'segments': segments
                    })
                
                return {
                    'origin': route.get('origin'),
                    'destination': route.get('destination'),
                    'count': len(transits),
                    'transits': transits,
                    'plans': plans
                }
            else:
                print(f"[公交规划] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[公交规划] 异常: {e}")
            return None
    
    async def get_bicycling_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[Dict]:
        """
        获取骑行路线（v5 API）
        
        Args:
            origin: 起点 (lng, lat)
            destination: 终点 (lng, lat)
            
        Returns:
            骑行路线信息
        """
        url = f"{self.base_url}/direction/bicycling"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'show_fields': 'cost,polyline'
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route', {})
                paths = route.get('paths', [])
                
                if paths:
                    path = paths[0]
                    cost = path.get('cost', {})
                    
                    return {
                        'distance': int(path.get('distance', 0)),
                        'duration': int(cost.get('duration', 0)),
                        'paths': paths,
                        'polyline': path.get('polyline', '')
                    }
            else:
                print(f"[骑行规划] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[骑行规划] 异常: {e}")
            return None
    
    async def get_electrobike_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Optional[Dict]:
        """
        获取电动车路线（v5 API）
        
        Args:
            origin: 起点 (lng, lat)
            destination: 终点 (lng, lat)
            
        Returns:
            电动车路线信息
        """
        url = f"{self.base_url}/direction/electrobike"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'show_fields': 'cost,polyline'
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route', {})
                paths = route.get('paths', [])
                
                if paths:
                    path = paths[0]
                    cost = path.get('cost', {})
                    
                    return {
                        'distance': int(path.get('distance', 0)),
                        'duration': int(cost.get('duration', 0)),
                        'paths': paths,
                        'polyline': path.get('polyline', '')
                    }
            else:
                print(f"[电动车规划] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[电动车规划] 异常: {e}")
            return None

