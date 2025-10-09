"""
地图服务：封装高德API调用
"""
import httpx
from typing import List, Dict, Optional, Tuple
from app.core.config import settings


class MapService:
    """地图服务：封装高德API调用"""
    
    def __init__(self):
        self.api_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def search_attractions(
        self, 
        city: str, 
        keyword: str = "景点",
        types: str = "110000",
        limit: int = 25
    ) -> List[Dict]:
        """
        搜索景点（调用高德POI API）
        
        Args:
            city: 城市名称
            keyword: 搜索关键词
            types: 类型编码（110000=旅游景点）
            limit: 返回数量
            
        Returns:
            景点列表
        """
        url = f"{self.base_url}/place/text"
        
        params = {
            'key': self.api_key,
            'keywords': keyword,
            'city': city,
            'types': types,
            'offset': limit,
            'extensions': 'all'
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        if data['status'] == '1':
            pois = data.get('pois', [])
            
            # 格式化景点数据
            attractions = []
            for poi in pois:
                location = poi['location'].split(',')
                
                # 提取评分和价格
                biz_ext = poi.get('biz_ext', {})
                rating = 0.0
                cost = "未知"
                
                if isinstance(biz_ext, dict):
                    # rating可能是字符串或数字
                    rating_value = biz_ext.get('rating', 0)
                    if rating_value and str(rating_value).strip():
                        try:
                            rating = float(rating_value)
                        except:
                            rating = 0.0
                    
                    # cost可能是字符串、数字或数组
                    cost_value = biz_ext.get('cost', '未知')
                    if isinstance(cost_value, list):
                        cost = '未知' if not cost_value else str(cost_value[0])
                    else:
                        cost = str(cost_value) if cost_value else '未知'
                
                # 处理photos - 提取URL
                photos_data = poi.get('photos', [])
                photos = []
                if isinstance(photos_data, list):
                    for photo in photos_data:
                        if isinstance(photo, dict):
                            url = photo.get('url', '')
                            if url:
                                photos.append(url)
                        elif isinstance(photo, str):
                            photos.append(photo)
                
                # 处理tel - 可能是字符串或数组
                tel_value = poi.get('tel', '')
                if isinstance(tel_value, list):
                    tel = tel_value[0] if tel_value else ''
                else:
                    tel = str(tel_value) if tel_value else ''
                
                attractions.append({
                    'id': poi['id'],
                    'name': poi['name'],
                    'lng': float(location[0]),
                    'lat': float(location[1]),
                    'type': poi.get('type', ''),
                    'typecode': poi.get('typecode', ''),
                    'address': poi.get('address', ''),
                    'city': city,
                    'rating': rating,
                    'cost': cost,
                    'tel': tel,
                    'photos': photos
                })
            
            return attractions
        else:
            raise Exception(f"高德API错误: {data.get('info')}")
    
    async def get_distance_matrix(
        self, 
        origins: List[Tuple[float, float]], 
        destinations: List[Tuple[float, float]],
        type: int = 3  # 1=驾车, 3=步行
    ) -> List[List[Dict]]:
        """
        获取距离矩阵（调用高德距离API）
        
        Args:
            origins: 起点坐标列表 [(lng, lat), ...]
            destinations: 终点坐标列表 [(lng, lat), ...]
            type: 类型（1=驾车, 3=步行）
            
        Returns:
            距离矩阵
        """
        url = f"{self.base_url}/distance"
        
        # 由于高德API限制，需要分批请求
        # 每次最多100个起点和终点的组合
        results = []
        
        for origin in origins:
            origins_str = f"{origin[0]},{origin[1]}"
            destinations_str = "|".join([f"{d[0]},{d[1]}" for d in destinations])
            
            params = {
                'key': self.api_key,
                'origins': origins_str,
                'destination': destinations_str,
                'type': type
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data['status'] == '1':
                results.append(data['results'])
            else:
                raise Exception(f"高德API错误: {data.get('info')}")
        
        return results
    
    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = 'walking'  # walking, driving, transit
    ) -> Dict:
        """
        获取路径规划（调用高德路径规划API）
        
        Args:
            origin: 起点坐标 (lng, lat)
            destination: 终点坐标 (lng, lat)
            mode: 出行方式
            
        Returns:
            路线数据
        """
        mode_map = {
            'walking': 'walking',
            'driving': 'driving',
            'transit': 'integrated'
        }
        
        url = f"{self.base_url}/direction/{mode_map[mode]}"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        if data['status'] == '1':
            route = data['route']
            
            # 提取关键信息
            if mode == 'walking':
                paths = route.get('paths', [])
                if paths:
                    path = paths[0]
                    return {
                        'distance': float(path.get('distance', 0)),  # 米
                        'duration': float(path.get('duration', 0)),  # 秒
                        'steps': path.get('steps', []),
                        'polyline': path.get('polyline', '')
                    }
            elif mode == 'driving':
                paths = route.get('paths', [])
                if paths:
                    path = paths[0]
                    return {
                        'distance': float(path.get('distance', 0)),
                        'duration': float(path.get('duration', 0)),
                        'steps': path.get('steps', []),
                        'polyline': path.get('polyline', '')
                    }
            
            return {
                'distance': 0,
                'duration': 0,
                'steps': [],
                'polyline': ''
            }
        else:
            raise Exception(f"高德API错误: {data.get('info')}")
    
    def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        计算两点间的直线距离（Haversine公式）
        
        Args:
            point1: 点1坐标 (lng, lat)
            point2: 点2坐标 (lng, lat)
            
        Returns:
            距离（米）
        """
        from math import radians, sin, cos, sqrt, atan2
        
        lng1, lat1 = point1
        lng2, lat2 = point2
        
        # 地球半径（米）
        R = 6371000
        
        # 转换为弧度
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lng = radians(lng2 - lng1)
        
        # Haversine公式
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c
        
        return distance

