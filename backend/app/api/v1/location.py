"""
IP定位API（优化版）
自动识别真实IP，兼容CDN、反向代理等场景
"""
from fastapi import APIRouter, Request
from typing import Optional

from app.services.map_service import MapService
from app.core.ip_utils import get_real_ip, get_ip_info, is_private_ip

router = APIRouter()
map_service = MapService()


@router.get("/ip")
async def get_location_by_ip(request: Request, ip: Optional[str] = None):
    """
    IP定位：智能获取用户位置（自动识别真实IP）
    
    功能：
    - 自动识别客户端真实IP
    - 支持Cloudflare CDN (CF-Connecting-IP)
    - 支持Nginx (X-Real-IP, X-Forwarded-For)
    - 支持阿里云CDN (Ali-CDN-Real-IP)
    - 支持阿里云SLB (X-Cluster-Client-IP)
    - 支持多层代理场景
    - 返回城市中心坐标（用于地图居中）
    
    Args:
        ip: IP地址（可选）。如果不填，自动智能识别客户端真实IP
        
    Returns:
        {
            'status': 'success',
            'province': '省份名称',
            'city': '城市名称', 
            'adcode': '区域编码',
            'location': {
                'lng': 经度,
                'lat': 纬度
            },
            'ip': '实际使用的IP地址',
            'is_private': false
        }
        
    示例：
        GET /api/v1/location/ip （自动获取）
        GET /api/v1/location/ip?ip=114.247.50.2 （手动指定）
    """
    # 如果没有指定IP，智能获取客户端真实IPv4地址
    if not ip:
        ip = get_real_ip(request)
        
        if ip:
            print(f"[IP定位] 智能识别客户端IPv4: {ip}")
            
            # 如果是内网IP，使用高德API自动识别
            if is_private_ip(ip):
                print(f"[IP定位] 检测到内网IP: {ip}，让高德API自动识别")
                ip = None  # 传None给高德，让高德API自动识别请求来源IP
        else:
            # 未找到IPv4地址（可能是IPv6网络）
            print(f"[IP定位] 未找到IPv4地址，可能是IPv6网络，让高德API自动识别")
            ip = None
    else:
        print(f"[IP定位] 使用手动指定IP: {ip}")
    
    try:
        # 调用高德IP定位API
        location_data = await map_service.get_location_by_ip(ip)
        
        if location_data:
            # 格式化返回数据
            result = {
                'status': 'success',
                'province': location_data['province'],
                'city': location_data['city'],
                'adcode': location_data['adcode'],
                'ip': ip if ip else '服务器自动识别',
                'is_private': is_private_ip(ip) if ip else False
            }
            
            # 添加中心坐标（如果有）
            if location_data.get('location'):
                lng, lat = location_data['location']
                result['location'] = {
                    'lng': lng,
                    'lat': lat
                }
                print(f"[IP定位] 成功: {location_data['city']} ({lng}, {lat})")
            else:
                result['location'] = None
                print(f"[IP定位] 成功: {location_data['city']} (无坐标)")
            
            # 添加矩形区域（可选）
            if location_data.get('rectangle'):
                result['rectangle'] = location_data['rectangle']
            
            return result
        else:
            # 定位失败，返回默认位置（北京）
            print(f"[IP定位] 失败，使用默认位置")
            return {
                'status': 'fallback',
                'province': '北京',
                'city': '北京',
                'adcode': '110000',
                'location': {
                    'lng': 116.397428,  # 天安门
                    'lat': 39.90923
                },
                'ip': ip if ip else 'unknown',
                'message': 'IP定位失败，使用默认位置（北京）'
            }
            
    except Exception as e:
        print(f"[IP定位API] 异常: {e}")
        import traceback
        traceback.print_exc()
        
        # 异常时返回默认位置
        return {
            'status': 'error',
            'province': '北京',
            'city': '北京',
            'adcode': '110000',
            'location': {
                'lng': 116.397428,
                'lat': 39.90923
            },
            'ip': ip if ip else 'unknown',
            'error': str(e),
            'message': '定位服务异常，使用默认位置'
        }


@router.get("/test")
async def test_ip_location(ip: str):
    """
    测试IP定位（指定IP）
    
    用于测试不同IP地址的定位结果
    
    Args:
        ip: 要测试的IP地址
        
    示例:
        GET /api/v1/location/test?ip=114.247.50.2 （上海）
        GET /api/v1/location/test?ip=113.108.209.9 （广州）
        GET /api/v1/location/test?ip=192.168.1.1 （局域网）
    """
    print(f"[IP定位测试] IP: {ip}")
    
    location_data = await map_service.get_location_by_ip(ip)
    
    if location_data:
        return {
            'status': 'success',
            'data': location_data,
            'is_private': is_private_ip(ip)
        }
    else:
        return {
            'status': 'failed',
            'message': 'IP定位失败（可能是局域网IP或国外IP）',
            'ip': ip,
            'is_private': is_private_ip(ip)
        }


@router.get("/debug")
async def debug_ip_headers(request: Request):
    """
    调试IP获取（显示所有相关请求头）
    
    用于调试和排查IP获取问题
    
    Returns:
        所有IP相关的请求头信息
    """
    ip_info = get_ip_info(request)
    
    return {
        'detected_ip': ip_info['real_ip'],
        'is_private': ip_info['is_private'],
        'all_headers': ip_info['headers'],
        'client_host': ip_info['client_host'],
        'recommendation': '如果detected_ip为None或内网IP，请检查代理配置'
    }
