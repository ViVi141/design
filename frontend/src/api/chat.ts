/**
 * AI对话API
 */
import request from './index'

export interface ChatMessage {
  role: string
  content: string
}

export interface ChatRequest {
  message: string
  history?: ChatMessage[]
}

export interface TravelRequirements {
  destination: string
  days: number
  budget?: number
  preferences: string[]
  start_date?: string
}

/**
 * AI对话
 */
export const chat = (data: ChatRequest) => {
  return request.post('/chat/chat', data)
}

/**
 * 提取旅行需求
 */
export const extractRequirements = (message: string) => {
  return request.post<TravelRequirements>('/chat/extract', { message })
}

/**
 * 生成旅行攻略
 */
export const generateGuide = (data: any) => {
  return request.post('/chat/guide', data)
}

