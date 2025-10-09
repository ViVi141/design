/**
 * 路线规划API（v5）
 */
import request from './index'

export interface RouteRequest {
  origin: [number, number]
  destination: [number, number]
  mode: 'driving' | 'walking' | 'bicycling' | 'electrobike' | 'transit'
  strategy?: number
  city?: string
}

export interface DrivingResult {
  distance: number
  duration: number
  tolls: number
  traffic_lights: number
  taxi_cost: string
  polyline: string
}

export interface WalkingResult {
  distance: number
  duration: number
  polyline: string
}

export interface TransitResult {
  count: number
  transits: any[]
  plans: Array<{
    distance: number
    duration: number
    transit_fee: number
    walking_distance: number
    lines: Array<{
      name: string
      type: string
      via_num: number
    }>
  }>
}

/**
 * 规划路线
 */
export const planRoute = (data: RouteRequest) => {
  return request.post('/route/plan', data)
}

/**
 * 获取策略列表
 */
export const getStrategies = () => {
  return request.get('/route/strategies')
}

/**
 * 驾车策略
 */
export const DrivingStrategy = {
  SPEED_PRIORITY: 0,      // 速度优先
  FEE_PRIORITY: 1,        // 费用优先
  NORMAL_FAST: 2,         // 常规最快
  DEFAULT: 32,            // 默认推荐
  AVOID_CONGESTION: 33,   // 躲避拥堵
  HIGHWAY_PRIORITY: 34,   // 高速优先
  NO_HIGHWAY: 35,         // 不走高速
  LESS_FEE: 36,           // 少收费
  MAIN_ROAD: 37,          // 大路优先
  FASTEST: 38             // 速度最快
}

/**
 * 公交策略
 */
export const TransitStrategy = {
  RECOMMEND: 0,           // 推荐模式
  CHEAPEST: 1,            // 最经济
  LEAST_TRANSFER: 2,      // 最少换乘
  LEAST_WALKING: 3,       // 最少步行
  COMFORTABLE: 4,         // 最舒适
  NO_SUBWAY: 5,           // 不乘地铁
  SUBWAY_MAP: 6,          // 地铁图模式
  SUBWAY_PRIORITY: 7,     // 地铁优先
  TIME_SHORT: 8           // 时间短
}

