/**
 * 景点API
 */
import request from './index'

export interface AttractionSearch {
  city: string
  keyword?: string
  types?: string
  limit?: number
}

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
}

/**
 * 搜索景点
 */
export const searchAttractions = (data: AttractionSearch) => {
  return request.post<Attraction[]>('/attractions/search', data)
}

/**
 * 推荐景点
 */
export const recommendAttractions = (params: { city: string; preferences?: string; limit?: number }) => {
  return request.get('/attractions/recommend', { params })
}

