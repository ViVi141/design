"""
IP地址获取工具
兼容各种代理、CDN、负载均衡场景
"""
from fastapi import Request
from typing import Optional


def get_real_ip(request: Request) -> Optional[str]:
    """
    获取客户端真实IP地址（仅IPv4）
    
    支持场景：
    - 直连
    - Nginx反向代理
    - CDN（Cloudflare, 阿里云CDN等）
    - 负载均衡
    - 多层代理
    
    注意：自动过滤IPv6地址（高德API不支持）
    
    Args:
        request: FastAPI Request对象
        
    Returns:
        客户端真实IPv4地址，如果是IPv6则返回None
    """
    
    # 优先级1: CF-Connecting-IP（Cloudflare CDN）
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip and not is_ipv6(cf_ip) and is_valid_ip(cf_ip):
        return cf_ip
    
    # 优先级2: X-Real-IP（Nginx常用）
    real_ip = request.headers.get('X-Real-IP')
    if real_ip and not is_ipv6(real_ip) and is_valid_ip(real_ip):
        return real_ip
    
    # 优先级3: X-Forwarded-For（标准代理头）
    # 格式: client, proxy1, proxy2
    # 取第一个非内网的IPv4地址
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        ips = [ip.strip() for ip in forwarded_for.split(',')]
        for ip in ips:
            if not is_ipv6(ip) and is_valid_ip(ip) and not is_private_ip(ip):
                return ip
    
    # 优先级4: X-Forwarded（非标准）
    forwarded = request.headers.get('X-Forwarded')
    if forwarded and not is_ipv6(forwarded) and is_valid_ip(forwarded):
        return forwarded
    
    # 优先级5: Forwarded（RFC 7239标准）
    forwarded_std = request.headers.get('Forwarded')
    if forwarded_std:
        # 格式: for=192.0.2.60;proto=http;by=203.0.113.43
        import re
        match = re.search(r'for=([^;,\s]+)', forwarded_std)
        if match:
            ip = match.group(1).strip('"[]')
            if not is_ipv6(ip) and is_valid_ip(ip):
                return ip
    
    # 优先级6: X-Client-IP
    client_ip = request.headers.get('X-Client-IP')
    if client_ip and not is_ipv6(client_ip) and is_valid_ip(client_ip):
        return client_ip
    
    # 优先级7: X-Cluster-Client-IP（阿里云SLB）
    cluster_ip = request.headers.get('X-Cluster-Client-IP')
    if cluster_ip and not is_ipv6(cluster_ip) and is_valid_ip(cluster_ip):
        return cluster_ip
    
    # 优先级8: Ali-CDN-Real-IP（阿里云CDN）
    ali_cdn_ip = request.headers.get('Ali-CDN-Real-IP')
    if ali_cdn_ip and not is_ipv6(ali_cdn_ip) and is_valid_ip(ali_cdn_ip):
        return ali_cdn_ip
    
    # 优先级9: request.client（直连）
    if request.client and request.client.host:
        client_host = request.client.host
        if not is_ipv6(client_host) and is_valid_ip(client_host):
            return client_host
    
    # 无法获取有效IPv4地址，返回None
    print("[IP工具] 未找到有效的IPv4地址（可能是IPv6网络）")
    return None


def is_ipv6(ip: str) -> bool:
    """
    检查是否为IPv6地址
    
    Args:
        ip: IP地址字符串
        
    Returns:
        是否为IPv6地址
    """
    if not ip:
        return False
    
    # IPv6包含冒号且有多个
    return ':' in ip and ip.count(':') >= 2


def is_valid_ip(ip: str) -> bool:
    """
    验证IP地址格式是否有效（仅IPv4）
    
    Args:
        ip: IP地址字符串
        
    Returns:
        是否为有效的IPv4地址
    """
    if not ip:
        return False
    
    # 排除IPv6
    if is_ipv6(ip):
        return False
    
    # 移除可能的端口号
    if ':' in ip:
        ip = ip.split(':')[0]
    
    parts = ip.split('.')
    
    if len(parts) != 4:
        return False
    
    try:
        for part in parts:
            num = int(part)
            if num < 0 or num > 255:
                return False
        return True
    except ValueError:
        return False


def is_private_ip(ip: str) -> bool:
    """
    判断是否为内网IP
    
    Args:
        ip: IP地址
        
    Returns:
        是否为内网IP
    """
    if not is_valid_ip(ip):
        return False
    
    parts = [int(p) for p in ip.split('.')]
    
    # 10.0.0.0 - 10.255.255.255
    if parts[0] == 10:
        return True
    
    # 172.16.0.0 - 172.31.255.255
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return True
    
    # 192.168.0.0 - 192.168.255.255
    if parts[0] == 192 and parts[1] == 168:
        return True
    
    # 127.0.0.0 - 127.255.255.255 (localhost)
    if parts[0] == 127:
        return True
    
    # 169.254.0.0 - 169.254.255.255 (链路本地地址)
    if parts[0] == 169 and parts[1] == 254:
        return True
    
    return False


def get_ip_info(request: Request) -> dict:
    """
    获取IP详细信息（用于调试）
    
    Args:
        request: FastAPI Request对象
        
    Returns:
        包含所有可能IP来源的字典
    """
    real_ip = get_real_ip(request)
    
    return {
        'real_ip': real_ip,
        'is_private': is_private_ip(real_ip) if real_ip else None,
        'headers': {
            'CF-Connecting-IP': request.headers.get('CF-Connecting-IP'),
            'X-Real-IP': request.headers.get('X-Real-IP'),
            'X-Forwarded-For': request.headers.get('X-Forwarded-For'),
            'X-Forwarded': request.headers.get('X-Forwarded'),
            'Forwarded': request.headers.get('Forwarded'),
            'X-Client-IP': request.headers.get('X-Client-IP'),
            'X-Cluster-Client-IP': request.headers.get('X-Cluster-Client-IP'),
            'Ali-CDN-Real-IP': request.headers.get('Ali-CDN-Real-IP'),
        },
        'client_host': request.client.host if request.client else None
    }

