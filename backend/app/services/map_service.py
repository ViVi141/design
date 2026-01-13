"""
地图服务：封装高德API调用
"""
import httpx
from typing import List, Dict, Optional, Tuple
from app.core.config import settings


class MapService:
    """地图服务：封装高德API调用"""
    
    def __init__(self):
        # Web服务API Key（用于后端REST API调用）
        self.api_key = "your_key"
        self.base_url = "https://restapi.amap.com/v3"
    
    async def search_attractions_v5(
        self, 
        keywords: str,
        region: str = None,
        types: str = None,
        city_limit: bool = False,
        page_size: int = 25,
        page_num: int = 1,
        show_fields: str = "business,photos,navi"
    ) -> List[Dict]:
        """
        搜索景点（使用v5 POI搜索2.0）
        
        Args:
            keywords: 搜索关键词
            region: 搜索区划（城市名称/citycode/adcode）
            types: POI类型编码
            city_limit: 是否仅返回指定城市数据
            page_size: 每页数量(1-25)
            page_num: 页码
            show_fields: 返回字段控制 business,photos,navi,children,indoor
            
        Returns:
            景点列表
        """
        url = "https://restapi.amap.com/v5/place/text"
        
        params = {
            'key': self.api_key,
            'keywords': keywords,
            'page_size': page_size,
            'page_num': page_num,
            'show_fields': show_fields
        }
        
        if region:
            params['region'] = region
        
        if types:
            params['types'] = types
        
        if city_limit:
            params['city_limit'] = 'true'
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
        
        # 简化日志（仅在出错时打印详细信息）
        if data.get('status') != '1':
            print(f"[POI搜索v5] 错误 - 状态: {data.get('status')}, 信息: {data.get('info')}")
            print(f"[POI搜索v5] 请求参数: {params}")
        
        if data['status'] == '1':
            pois = data.get('pois', [])
            
            # 格式化景点数据
            attractions = []
            for poi in pois:
                try:
                    location = poi['location'].split(',')
                    
                    # 提取评分和价格（v5 API在business对象下）
                    business = poi.get('business', {})
                    rating = 0.0
                    cost = "未知"
                    tel = ''
                    
                    if isinstance(business, dict):
                        # 提取rating（餐饮、酒店、景点、影院类POI）
                        rating_value = business.get('rating', '')
                        if rating_value and str(rating_value).strip():
                            try:
                                rating = float(rating_value)
                            except:
                                rating = 0.0
                        
                        # 提取cost人均消费（餐饮、酒店、景点、影院类POI）
                        cost_value = business.get('cost', '')
                        if cost_value and str(cost_value).strip():
                            cost = str(cost_value)
                        
                        # 提取电话
                        tel_value = business.get('tel', '')
                        if isinstance(tel_value, list):
                            tel = tel_value[0] if tel_value else ''
                        else:
                            tel = str(tel_value) if tel_value else ''
                    
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
                    
                    # 获取第一张图片作为缩略图
                    thumbnail = photos[0] if photos else ''
                    
                    attractions.append({
                        'id': poi['id'],
                        'name': poi['name'],
                        'lng': float(location[0]),
                        'lat': float(location[1]),
                        'type': poi.get('type', ''),
                        'typecode': poi.get('typecode', ''),
                        'address': poi.get('address', ''),
                        'city': poi.get('city', region) if poi.get('city') else region,
                        'rating': rating,
                        'cost': cost,
                        'tel': tel,
                        'photos': photos,  # 所有图片
                        'thumbnail': thumbnail  # 缩略图（第一张）
                    })
                except Exception as e:
                    # 单个POI数据异常，跳过，不影响其他POI
                    print(f"[POI解析] 跳过异常POI: {poi.get('name', 'unknown')}, 错误: {e}")
                    continue
            
            return attractions
        else:
            raise Exception(f"高德API错误: {data.get('info')}")
    
    # 省级到省会的映射
    PROVINCE_CAPITAL_MAP = {
        '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
        '河北': '石家庄', '山西': '太原', '辽宁': '沈阳', '吉林': '长春', '黑龙江': '哈尔滨',
        '江苏': '南京', '浙江': '杭州', '安徽': '合肥', '福建': '福州', '江西': '南昌',
        '山东': '济南', '河南': '郑州', '湖北': '武汉', '湖南': '长沙', '广东': '广州',
        '海南': '海口', '四川': '成都', '贵州': '贵阳', '云南': '昆明', '陕西': '西安',
        '甘肃': '兰州', '青海': '西宁', '台湾': '台北', '内蒙古': '呼和浩特',
        '广西': '南宁', '西藏': '拉萨', '宁夏': '银川', '新疆': '乌鲁木齐', '香港': '香港',
        '澳门': '澳门'
    }
    
    async def get_weather(self, city: str) -> Optional[Dict]:
        """
        获取城市天气预报（未来7天）
        支持：城市名、省级名（自动转换为省会）
        """
        try:
            # 如果是省级名称，转换为省会
            if city in self.PROVINCE_CAPITAL_MAP:
                capital = self.PROVINCE_CAPITAL_MAP[city]
                print(f"[天气API] 省级转换：{city} → {capital}")
                city = capital
            
            print(f"[天气API] 开始查询：{city}")
            
            # 1. 获取城市adcode
            district_url = f"{self.base_url}/config/district"
            async with httpx.AsyncClient(timeout=10.0) as client:
                print(f"[天气API] 步骤1：获取城市adcode")
                response = await client.get(district_url, params={
                    'key': self.api_key,
                    'keywords': city,
                    'subdistrict': 0
                })
                data = response.json()
                print(f"[天气API] 行政区查询响应: status={data.get('status')}, districts数量={len(data.get('districts', []))}")
                
                if data.get('status') != '1' or not data.get('districts'):
                    print(f"[天气API] 未找到城市：{city}")
                    return None
                
                adcode = data['districts'][0]['adcode']
                city_name = data['districts'][0]['name']
                print(f"[天气API] 城市adcode: {adcode}, 名称: {city_name}")
                
                # 2. 获取天气信息
                weather_url = f"{self.base_url}/weather/weatherInfo"
                print(f"[天气API] 步骤2：获取天气预报")
                response = await client.get(weather_url, params={
                    'key': self.api_key,
                    'city': adcode,
                    'extensions': 'all'
                })
                weather_data = response.json()
                print(f"[天气API] 天气查询响应: status={weather_data.get('status')}, info={weather_data.get('info')}")
                
                if weather_data.get('status') != '1':
                    print(f"[天气API] 天气查询失败：{weather_data.get('info')}")
                    return None
                
                forecasts = weather_data.get('forecasts', [])
                if not forecasts:
                    return None
                
                forecast = forecasts[0]
                casts = forecast.get('casts', [])
                
                # 格式化数据
                return {
                    'city': forecast.get('city'),
                    'forecasts': [{
                        'date': c.get('date'),
                        'week': c.get('week'),
                        'day_weather': c.get('dayweather'),
                        'night_weather': c.get('nightweather'),
                        'day_temp': c.get('daytemp'),
                        'night_temp': c.get('nighttemp'),
                        'day_wind': c.get('daywind'),
                        'day_power': c.get('daypower')
                    } for c in casts[:7]]
                }
                
        except Exception as e:
            print(f"[天气API] 异常: {e}")
            return None
    
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
    
    async def get_route_v5(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving",
        strategy: int = None,
        city: str = None,
        show_fields: str = "cost,navi,polyline"
    ) -> Optional[Dict]:
        """
        获取路线规划（使用v5 API - 路径规划2.0）
        
        Args:
            origin: 起点坐标 (lng, lat)
            destination: 终点坐标 (lng, lat)
            mode: 出行方式 driving/walking/bicycling/electrobike/transit
            strategy: 驾车策略 32=默认推荐，38=速度最快，0=速度优先
            city: 城市citycode（transit需要）
            show_fields: 返回字段控制 cost,navi,polyline
            
        Returns:
            路线信息 {distance, duration, paths, tolls, traffic_lights, ...}
        """
        base_url = "https://restapi.amap.com/v5"
        
        # 构建URL
        if mode == "transit":
            url = f"{base_url}/direction/transit/integrated"
        else:
            url = f"{base_url}/direction/{mode}"
        
        params = {
            'key': self.api_key,
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'show_fields': show_fields
        }
        
        # 驾车特有参数
        if mode == "driving":
            params['strategy'] = strategy if strategy is not None else 32  # 默认推荐
            params['ferry'] = 0  # 使用轮渡
        
        # 步行特有参数
        if mode == "walking":
            params['alternative_route'] = 1  # 返回1条路线
        
        # 公交特有参数
        if mode == "transit":
            if not city:
                city = "010"  # 默认北京citycode
            params['city1'] = city
            params['city2'] = city
            params['strategy'] = 0  # 0=推荐，1=最经济，2=最少换乘，8=时间短
            params['AlternativeRoute'] = 3  # 返回3条方案
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                route = data.get('route')
                print(f"[路径规划v5] {mode}路线规划成功")
                return route
            else:
                print(f"[路径规划v5] 错误: {data.get('info')}, infocode: {data.get('infocode')}")
                return None
        except Exception as e:
            print(f"[路径规划v5] 异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_input_tips(
        self,
        keywords: str,
        city: str = None,
        location: Tuple[float, float] = None,
        datatype: str = "all",
        citylimit: bool = False
    ) -> List[Dict]:
        """
        获取输入提示（自动补全建议）
        
        Args:
            keywords: 查询关键词
            city: 城市（citycode或adcode）
            location: 优先返回此坐标附近的结果
            datatype: 数据类型 all/poi/bus/busline
            citylimit: 是否仅返回指定城市数据
            
        Returns:
            建议列表
        """
        url = f"{self.base_url}/assistant/inputtips"
        
        params = {
            'key': self.api_key,
            'keywords': keywords,
            'output': 'json'
        }
        
        if city:
            params['city'] = city
        
        if location:
            params['location'] = f"{location[0]},{location[1]}"
        
        if datatype:
            params['datatype'] = datatype
        
        if citylimit:
            params['citylimit'] = 'true'
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                tips = data.get('tips', [])
                return tips
            else:
                print(f"[输入提示] 错误: {data.get('info')}")
                return []
        except Exception as e:
            print(f"[输入提示] 异常: {e}")
            return []
    
    async def search_around(
        self,
        location: Tuple[float, float],
        keywords: str = None,
        types: str = None,
        radius: int = 5000,
        region: str = None,
        city_limit: bool = False,
        sortrule: str = "distance",
        page_size: int = 25
    ) -> List[Dict]:
        """
        周边搜索（v5 API）
        
        Args:
            location: 中心点坐标 (lng, lat)
            keywords: 关键词
            types: POI类型
            radius: 半径(0-50000米)
            region: 区域
            city_limit: 是否限制在指定城市
            sortrule: 排序规则 distance/weight
            page_size: 每页数量
            
        Returns:
            POI列表
        """
        url = "https://restapi.amap.com/v5/place/around"
        
        params = {
            'key': self.api_key,
            'location': f"{location[0]},{location[1]}",
            'radius': radius,
            'sortrule': sortrule,
            'page_size': page_size,
            'show_fields': 'business,photos'
        }
        
        if keywords:
            params['keywords'] = keywords
        
        if types:
            params['types'] = types
        
        if region:
            params['region'] = region
        
        if city_limit:
            params['city_limit'] = 'true'
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                pois = data.get('pois', [])
                return self._parse_pois_v5(pois)
            else:
                print(f"[周边搜索] 错误: {data.get('info')}")
                return []
        except Exception as e:
            print(f"[周边搜索] 异常: {e}")
            return []
    
    async def get_poi_detail(
        self,
        poi_ids: List[str],
        show_fields: str = "business,photos,navi,children"
    ) -> List[Dict]:
        """
        ID搜索（v5 API）
        
        Args:
            poi_ids: POI ID列表（最多10个）
            show_fields: 返回字段控制
            
        Returns:
            POI详情列表
        """
        url = "https://restapi.amap.com/v5/place/detail"
        
        params = {
            'key': self.api_key,
            'id': '|'.join(poi_ids[:10]),
            'show_fields': show_fields
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            if data.get('status') == '1':
                pois = data.get('pois', [])
                return self._parse_pois_v5(pois)
            else:
                print(f"[POI详情] 错误: {data.get('info')}")
                return []
        except Exception as e:
            print(f"[POI详情] 异常: {e}")
            return []
    
    def _parse_pois_v5(self, pois: List[Dict]) -> List[Dict]:
        """解析v5 POI数据"""
        results = []
        for poi in pois:
            location = poi.get('location', '').split(',')
            if len(location) != 2:
                continue
            
            lng = float(location[0])
            lat = float(location[1])
            
            # 商业信息
            business = poi.get('business', {})
            rating = float(business.get('rating', 0)) if business.get('rating') else 0
            cost = business.get('cost', '')
            tel = business.get('tel', '')
            opentime = business.get('opentime_today', '')
            business_area = business.get('business_area', '')
            
            # 图片
            photos = []
            photos_data = poi.get('photos', [])
            if photos_data:
                photos = [p.get('url', '') for p in photos_data if p.get('url')]
            
            # 缩略图（第一张图片）
            thumbnail = photos[0] if photos else ''
            
            # 导航信息
            navi = poi.get('navi', {})
            
            results.append({
                'id': poi.get('id', ''),
                'name': poi.get('name', ''),
                'lng': lng,
                'lat': lat,
                'type': poi.get('type', ''),
                'typecode': poi.get('typecode', ''),
                'address': poi.get('address', ''),
                'pname': poi.get('pname', ''),
                'cityname': poi.get('cityname', ''),
                'adname': poi.get('adname', ''),
                'pcode': poi.get('pcode', ''),
                'citycode': poi.get('citycode', ''),
                'adcode': poi.get('adcode', ''),
                'rating': rating,
                'cost': cost,
                'tel': tel,
                'opentime': opentime,
                'photos': photos,  # 所有图片列表
                'thumbnail': thumbnail,  # 缩略图（第一张）
                'business_area': business_area,
                'navi_poiid': navi.get('navi_poiid', ''),
                'entr_location': navi.get('entr_location', ''),
                'exit_location': navi.get('exit_location', '')
            })
        
        return results
    
    async def search_attractions(
        self, 
        city: str, 
        keyword: str = "景点",
        types: str = "110000",
        limit: int = 25
    ) -> List[Dict]:
        """
        搜索景点（兼容旧版本，调用v5）
        
        Args:
            city: 城市名称
            keyword: 搜索关键词
            types: 类型编码
            limit: 返回数量
            
        Returns:
            景点列表
        """
        return await self.search_attractions_v5(
            keywords=keyword,
            region=city,
            types=types,
            city_limit=True,
            page_size=min(limit, 25),
            show_fields="business,photos,navi"
        )
    
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
    
    async def get_location_by_ip(self, ip: str = None) -> Optional[Dict]:
        """
        IP定位：根据IP地址获取地理位置
        
        重要：如果不传ip参数，高德API会自动使用HTTP请求的来源IP（服务器出口IP）
        这对于本地开发或内网环境特别有用
        
        Args:
            ip: IP地址（可选）
                - 如果填写：使用指定IP定位
                - 如果不填：高德API自动使用请求来源IP（推荐）
            
        Returns:
            {
                'province': '省份',
                'city': '城市',
                'adcode': '区域编码',
                'rectangle': '矩形区域',
                'location': (lng, lat)  # 城市中心坐标
            }
        """
        url = f"{self.base_url}/ip"
        
        params = {
            'key': self.api_key,
            'output': 'json'
        }
        
        # 只有当ip不是内网IP时才传递
        if ip:
            # 检查是否为内网IP
            from app.core.ip_utils import is_private_ip
            if is_private_ip(ip):
                print(f"[IP定位] 检测到内网IP {ip}，不传递给高德API，让其自动识别")
                # 不设置ip参数，让高德API自动识别
            else:
                params['ip'] = ip
                print(f"[IP定位] 使用指定公网IP: {ip}")
        
        try:
            print(f"[IP定位] 调用高德API: {url}")
            print(f"[IP定位] 参数: {params}")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
            
            print(f"[IP定位] 响应状态: {data.get('status')}")
            print(f"[IP定位] 响应数据: {data}")
            
            if data.get('status') == '1':
                province = data.get('province', '')
                city = data.get('city', '')
                adcode = data.get('adcode', '')
                rectangle = data.get('rectangle', '')
                
                # 解析矩形区域，计算中心点
                location = None
                if rectangle:
                    # rectangle格式: "lng1,lat1;lng2,lat2"
                    try:
                        coords = rectangle.split(';')
                        if len(coords) == 2:
                            p1 = coords[0].split(',')
                            p2 = coords[1].split(',')
                            # 计算中心点
                            center_lng = (float(p1[0]) + float(p2[0])) / 2
                            center_lat = (float(p1[1]) + float(p2[1])) / 2
                            location = (center_lng, center_lat)
                    except:
                        pass
                
                return {
                    'province': province,
                    'city': city if city else province,  # 直辖市情况
                    'adcode': adcode,
                    'rectangle': rectangle,
                    'location': location,
                    'ip': ip if ip else '客户端IP'
                }
            else:
                print(f"[IP定位] 错误: {data.get('info')}")
                return None
        except Exception as e:
            print(f"[IP定位] 异常: {e}")
            return None

