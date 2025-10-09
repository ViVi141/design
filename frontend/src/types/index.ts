/**
 * 全局类型定义
 */

// 景点类型
export interface Attraction {
  id: string
  name: string
  lng: number
  lat: number
  city?: string
  address?: string
  type?: string
  rating?: number
  cost?: string
  tel?: string
  photos?: string[]
  distance?: number
}

// 行程类型
export interface Trip {
  id: number
  title: string
  destination: string
  days: number
  budget?: number
  attractions: Attraction[]
  routes?: RouteSegment[]
  summary?: TripSummary
  status: 'draft' | 'confirmed'
  created_at: string
  updated_at: string
}

// 路线段
export interface RouteSegment {
  from_idx: number
  to_idx: number
  from_name: string
  to_name: string
  distance: number
  duration: number
  mode: 'walking' | 'driving' | 'transit'
  polyline?: string
}

// 行程摘要
export interface TripSummary {
  num_attractions: number
  total_distance_km: number
  total_duration_hours: number
  total_cost: number
  optimization_rate?: number
}

// AI对话消息
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
}

// 旅行需求
export interface TravelRequirements {
  destination: string
  days: number
  budget?: number
  preferences: string[]
  start_date?: string
}

// API响应类型
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
}

