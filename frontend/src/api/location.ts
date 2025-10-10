/**
 * IP定位相关API
 */
import request from './index'

export interface IPLocationResponse {
  status: string
  province: string
  city: string
  adcode: string
  location: {
    lng: number
    lat: number
  } | null
  rectangle?: string
  ip?: string
  message?: string
}

/**
 * 获取当前IP的地理位置
 */
export function getIPLocation(): Promise<IPLocationResponse> {
  return request.get('/location/ip')
}

/**
 * 测试指定IP的地理位置
 */
export function testIPLocation(ip: string): Promise<IPLocationResponse> {
  return request.get(`/location/test?ip=${ip}`)
}

