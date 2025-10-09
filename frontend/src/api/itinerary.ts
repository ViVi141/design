/**
 * 完整行程规划API
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface GenerateRequest {
  destination: string
  days: number
  budget: number
  preferences?: string[]
  start_date?: string
}

export interface CompleteItinerary {
  daily_schedule: DaySchedule[]
  cost_breakdown: CostBreakdown
  packing_list: string[]
  travel_tips: string
}

export interface DaySchedule {
  day: number
  date?: string
  attractions: AttractionSchedule[]
  hotel?: HotelInfo
  transportation: TransportInfo[]
  meals_budget: number
}

export interface AttractionSchedule {
  name: string
  start_time: string
  duration_hours: number
  cost: number
  tips: string
}

export interface HotelInfo {
  name: string
  price_per_night: number
  address: string
  reason: string
}

export interface TransportInfo {
  type: string
  route?: string
  from_location: string
  to_location: string
  cost: number
  tips: string
}

export interface CostBreakdown {
  attractions: number
  hotels: number
  transportation: number
  meals: number
  total: number
  remaining: number
}

/**
 * 生成完整行程
 */
export async function generateCompleteItinerary(
  request: GenerateRequest
): Promise<CompleteItinerary> {
  const response = await axios.post(`${API_BASE}/itinerary/generate/complete`, request)
  return response.data
}

/**
 * 推荐住宿
 */
export async function recommendHotels(params: {
  destination: string
  central_location: string
  budget_per_night: number
  nights: number
}): Promise<HotelInfo[]> {
  const response = await axios.post(`${API_BASE}/itinerary/hotels/recommend`, params)
  return response.data
}

/**
 * 推荐交通方式
 */
export async function suggestTransportation(params: {
  from_city: string
  to_city: string
  date: string
  budget: number
}): Promise<TransportInfo[]> {
  const response = await axios.post(`${API_BASE}/itinerary/transportation/suggest`, params)
  return response.data
}

/**
 * 优化现有行程
 */
export async function optimizeItinerary(
  itinerary: CompleteItinerary,
  goal: string = '优化路线'
): Promise<CompleteItinerary> {
  const response = await axios.post(`${API_BASE}/itinerary/optimize`, {
    itinerary,
    goal
  })
  return response.data
}

/**
 * 预览目的地信息
 */
export async function previewDestination(destination: string): Promise<{
  recommended_days: number
  top_attractions_count: number
  avg_daily_budget: number
  best_season: string
  brief: string
}> {
  const response = await axios.get(`${API_BASE}/itinerary/preview/${destination}`)
  return response.data
}

