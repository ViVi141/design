/**
 * 地图状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Attraction } from '@/api/attraction'

export const useMapStore = defineStore('map', () => {
  // 地图实例
  const map = ref<any>(null)
  
  // 地图中心点
  const center = ref<[number, number]>([116.397428, 39.90923]) // 北京
  
  // 缩放级别
  const zoom = ref(12)
  
  // 景点列表
  const attractions = ref<Attraction[]>([])
  
  // 选中的景点
  const selectedAttractions = ref<Attraction[]>([])
  
  // 路线数据
  const routes = ref<any[]>([])
  
  // 设置地图实例
  const setMap = (mapInstance: any) => {
    map.value = mapInstance
  }
  
  // 设置中心点
  const setCenter = (lng: number, lat: number) => {
    center.value = [lng, lat]
    if (map.value) {
      map.value.setCenter([lng, lat])
    }
  }
  
  // 设置缩放
  const setZoom = (level: number) => {
    zoom.value = level
    if (map.value) {
      map.value.setZoom(level)
    }
  }
  
  // 添加景点
  const addAttraction = (attraction: Attraction) => {
    if (!selectedAttractions.value.find(a => a.id === attraction.id)) {
      selectedAttractions.value.push(attraction)
    }
  }
  
  // 移除景点
  const removeAttraction = (id: string) => {
    const index = selectedAttractions.value.findIndex(a => a.id === id)
    if (index > -1) {
      selectedAttractions.value.splice(index, 1)
    }
  }
  
  // 清空选中景点
  const clearSelectedAttractions = () => {
    selectedAttractions.value = []
  }
  
  // 设置路线
  const setRoutes = (routeData: any[]) => {
    routes.value = routeData
  }
  
  return {
    map,
    center,
    zoom,
    attractions,
    selectedAttractions,
    routes,
    setMap,
    setCenter,
    setZoom,
    addAttraction,
    removeAttraction,
    clearSelectedAttractions,
    setRoutes
  }
})

