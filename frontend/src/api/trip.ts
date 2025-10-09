/**
 * 行程API
 */
import request from './index'

export interface AttractionBase {
  name: string
  lng: number
  lat: number
  type?: string
  address?: string
  rating?: number
  cost?: string
}

export interface TripCreate {
  title: string
  destination: string
  days: number
  budget?: number
  attractions: AttractionBase[]
}

export interface Trip {
  id: number
  title: string
  destination: string
  days: number
  budget?: number
  attractions: any[]
  routes?: any[]
  summary?: any
  status: string
  created_at: string
  updated_at: string
}

/**
 * 创建行程
 */
export const createTrip = (data: TripCreate, optimize = true) => {
  return request.post<Trip>(`/trips/?optimize=${optimize}`, data)
}

/**
 * 获取行程列表
 */
export const getTrips = (params?: { skip?: number; limit?: number; destination?: string }) => {
  return request.get<Trip[]>('/trips/', { params })
}

/**
 * 获取单个行程
 */
export const getTrip = (id: number) => {
  return request.get<Trip>(`/trips/${id}`)
}

/**
 * 更新行程
 */
export const updateTrip = (id: number, data: Partial<TripCreate>) => {
  return request.put<Trip>(`/trips/${id}`, data)
}

/**
 * 删除行程
 */
export const deleteTrip = (id: number) => {
  return request.delete(`/trips/${id}`)
}

/**
 * 优化行程路径
 */
export const optimizeTrip = (id: number) => {
  return request.post<Trip>(`/trips/${id}/optimize`)
}

