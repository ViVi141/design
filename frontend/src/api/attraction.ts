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

/**
 * 获取输入提示（高德输入提示API）
 */
export const getInputTips = (params: { 
  keywords: string
  city?: string
  datatype?: string
  citylimit?: boolean
}) => {
  return request.get('/attractions/tips', { params })
}

/**
 * 周边搜索（v5 API）
 */
export const searchAround = (params: {
  location: string  // lng,lat
  keywords?: string
  types?: string
  radius?: number
  sortrule?: string
  page_size?: number
}) => {
  return request.get('/attractions/around', { params })
}

/**
 * POI详情查询（v5 API）
 */
export const getPoiDetail = (ids: string) => {
  return request.get('/attractions/detail', { params: { ids } })
}

