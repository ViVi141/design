<template>
  <div class="map-view">
    <el-row :gutter="20" style="height: 100%">
      <!-- 左侧：景点搜索和列表 -->
      <el-col :xs="24" :sm="8" :md="6" class="sidebar">
        <el-card>
          <template #header>
            <span>景点搜索</span>
          </template>
          
          <!-- 搜索表单 -->
          <el-form :model="searchForm" @submit.prevent="handleSearch">
            <el-form-item label="城市">
              <el-input v-model="searchForm.city" placeholder="请输入城市名称">
                <template #append>
                  <el-button @click="locateToMe" :loading="locating" title="定位到我">
                    <el-icon><Aim /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="如：景点、博物馆" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch" :loading="loading" style="width: 100%">
                <el-icon><Search /></el-icon>
                搜索景点
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 已选景点 -->
          <div v-if="selectedAttractions.length > 0" class="selected-section">
            <div class="section-header">
              <span>已选景点 ({{ selectedAttractions.length }})</span>
              <el-button text type="primary" @click="optimizeRoute" :loading="optimizing">
                <el-icon><MagicStick /></el-icon>
                优化路线
              </el-button>
            </div>
            <el-tag
              v-for="(item, index) in selectedAttractions"
              :key="item.id"
              closable
              @close="removeAttraction(item.id)"
              class="attraction-tag"
            >
              {{ index + 1 }}. {{ item.name }}
            </el-tag>
            <el-button type="success" @click="saveTrip" style="width: 100%; margin-top: 10px">
              <el-icon><Document /></el-icon>
              保存为行程
            </el-button>
          </div>

          <!-- 景点列表 -->
          <div class="attractions-list">
            <div class="section-header">
              <span>搜索结果</span>
            </div>
            <el-empty v-if="attractions.length === 0" description="暂无数据" />
            <div
              v-for="item in attractions"
              :key="item.id"
              class="attraction-item"
              @click="selectAttraction(item)"
            >
              <!-- 景点图片 -->
              <el-image
                v-if="item.photos && item.photos.length > 0"
                :src="item.photos[0]"
                fit="cover"
                class="attraction-image"
                :preview-src-list="item.photos"
              >
                <template #error>
                  <div class="image-slot">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div v-else class="image-placeholder">
                <el-icon size="40"><Picture /></el-icon>
              </div>
              
              <div class="attraction-info">
                <h4>{{ item.name }}</h4>
                <p class="address">{{ item.address }}</p>
                <div class="meta">
                  <el-rate v-if="item.rating" v-model="item.rating" disabled size="small" show-score />
                  <el-tag size="small" type="success" v-if="item.cost && item.cost !== '未知'">
                    💰 {{ item.cost }}
                  </el-tag>
                </div>
              </div>
              <el-button
                :type="isSelected(item.id) ? 'success' : 'primary'"
                size="small"
                circle
                :icon="isSelected(item.id) ? 'Check' : 'Plus'"
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：地图 -->
      <el-col :xs="24" :sm="16" :md="18" class="map-container">
        <el-card style="height: 100%">
          <div id="map" style="width: 100%; height: calc(100vh - 180px)"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 保存行程对话框 -->
    <el-dialog v-model="saveTripDialogVisible" title="保存行程" width="500px">
      <el-form :model="tripForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="tripForm.title" placeholder="给行程起个名字" />
        </el-form-item>
        <el-form-item label="目的地">
          <el-input v-model="tripForm.destination" />
        </el-form-item>
        <el-form-item label="天数">
          <el-input-number v-model="tripForm.days" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="预算">
          <el-input-number v-model="tripForm.budget" :min="0" /> 元
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveTripDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveTrip" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { Search, MagicStick, Document, Picture, Aim } from '@element-plus/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import { searchAttractions, type Attraction } from '@/api/attraction'
import { createTrip } from '@/api/trip'
import { useMapStore } from '@/stores/map'

const router = useRouter()
const mapStore = useMapStore()

const searchForm = ref({
  city: '北京',
  keyword: '景点'
})

const loading = ref(false)
const optimizing = ref(false)
const saving = ref(false)
const locating = ref(false)
const attractions = ref<Attraction[]>([])
const selectedAttractions = ref<Attraction[]>([])
const saveTripDialogVisible = ref(false)

const tripForm = ref({
  title: '',
  destination: '',
  days: 3,
  budget: 5000
})

let map: any = null
let markers: any[] = []
let polylines: any[] = []
let geolocationControl: any = null

// 初始化地图
const initMap = async () => {
  try {
    console.log('[地图] 初始化中...')
    
    // 加载高德地图
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.Geolocation']
    })

    // 初始化地图（默认北京）
    map = new AMap.Map('map', {
      zoom: 12,
      center: [116.397428, 39.90923],
      viewMode: '3D'
    })

    mapStore.setMap(map)
    
    // 使用高德官方Geolocation插件（但不自动执行）
    geolocationControl = new AMap.Geolocation({
      enableHighAccuracy: false,
      timeout: 10000,
      useNative: true,
      convert: true,
      showButton: false,
      showMarker: false,
      showCircle: false,
      panToLocation: true,
      zoomToAccuracy: false
    })
    
    map.addControl(geolocationControl)
    
    // 检测IPv6环境并提示
    checkIPv6AndNotify()
    
    console.log('地图初始化成功')
  } catch (error) {
    console.error('地图加载失败:', error)
    ElMessage.error('地图加载失败，请检查API密钥配置')
  }
}

// 检测IPv6环境并提示
const checkIPv6AndNotify = async () => {
  try {
    // 调用后端检测IP
    const response = await fetch('/api/v1/location/debug')
    const data = await response.json()
    
    const detectedIP = data.detected_ip
    const isPrivate = data.is_private
    
    // 判断是否为IPv6（包含冒号且冒号数量>=2）
    const isIPv6 = detectedIP && detectedIP.includes(':') && detectedIP.split(':').length >= 2
    
    if (isIPv6 || !detectedIP || isPrivate) {
      // 使用通知而不是消息框（更友好）
      ElNotification({
        title: '💡 自动定位提示',
        dangerouslyUseHTMLString: true,
        message: `
          <div style="line-height: 1.6;">
            <p><strong>检测到您的网络环境可能无法自动定位：</strong></p>
            ${isIPv6 ? '<p>• 您使用的是IPv6网络（高德API仅支持IPv4）</p>' : ''}
            ${isPrivate || !detectedIP ? '<p>• 您处于内网环境（如局域网）</p>' : ''}
            <p style="margin-top: 8px;"><strong>解决方案：</strong></p>
            <p>1️⃣ 点击城市输入框右侧的 <strong>📍定位按钮</strong>，使用浏览器定位</p>
            <p>2️⃣ 或直接在输入框中输入城市名称</p>
            <p style="color: #909399; font-size: 12px; margin-top: 8px;">
              提示：生产环境部署后，IPv4用户可以自动定位
            </p>
          </div>
        `,
        type: 'info',
        duration: 8000,
        position: 'top-right'
      })
    }
  } catch (error) {
    console.log('[IPv6检测] 检测失败，跳过提示')
  }
}

// 手动触发定位
const locateToMe = () => {
  if (!geolocationControl) {
    ElMessage.warning('定位功能未初始化')
    return
  }
  
  locating.value = true
  
  geolocationControl.getCurrentPosition((status: string, result: any) => {
    locating.value = false
    
    if (status === 'complete') {
      console.log('[定位] 成功:', result.position)
      ElMessage.success(`已定位到：${result.addressComponent?.city || '当前位置'}`)
      
      // 更新搜索表单城市
      if (result.addressComponent?.city) {
        searchForm.value.city = result.addressComponent.city
      }
    } else {
      console.log('[定位] 失败:', result.message)
      ElMessage.error('定位失败，请确保浏览器已允许位置访问权限')
    }
  })
}

// 搜索景点
const handleSearch = async () => {
  if (!searchForm.value.city) {
    ElMessage.warning('请输入城市名称')
    return
  }

  loading.value = true
  try {
    const data = await searchAttractions({
      city: searchForm.value.city,
      keyword: searchForm.value.keyword || '景点',
      limit: 25
    })
    attractions.value = data as Attraction[]
    
    // 在地图上显示标记
    showMarkersOnMap(attractions.value)
    
    // 调整地图视野
    if (attractions.value.length > 0) {
      const first = attractions.value[0]
      map?.setCenter([first.lng, first.lat])
    }
    
    ElMessage.success(`找到 ${attractions.value.length} 个景点`)
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

// 在地图上显示标记
const showMarkersOnMap = (items: Attraction[]) => {
  if (!map) return

  // 清除旧标记
  markers.forEach(marker => marker.setMap(null))
  markers = []

  // 创建新标记
  items.forEach(item => {
    const marker = new (window as any).AMap.Marker({
      position: [item.lng, item.lat],
      title: item.name,
      map: map
    })

    marker.on('click', () => {
      selectAttraction(item)
    })

    markers.push(marker)
  })
}

// 选择景点
const selectAttraction = (item: Attraction) => {
  const index = selectedAttractions.value.findIndex(a => a.id === item.id)
  if (index > -1) {
    selectedAttractions.value.splice(index, 1)
    ElMessage.info(`已取消选择：${item.name}`)
  } else {
    selectedAttractions.value.push(item)
    ElMessage.success(`已选择：${item.name}`)
  }
  
  // 更新地图显示
  highlightSelectedAttractions()
}

// 移除景点
const removeAttraction = (id: string) => {
  const index = selectedAttractions.value.findIndex(a => a.id === id)
  if (index > -1) {
    selectedAttractions.value.splice(index, 1)
    highlightSelectedAttractions()
  }
}

// 判断是否已选
const isSelected = (id: string) => {
  return selectedAttractions.value.some(a => a.id === id)
}

// 高亮选中的景点
const highlightSelectedAttractions = () => {
  // TODO: 实现高亮显示
}

// 优化路线
const optimizeRoute = async () => {
  if (selectedAttractions.value.length < 2) {
    ElMessage.warning('至少选择2个景点才能优化路线')
    return
  }

  optimizing.value = true
  try {
    // 这里调用后端API优化路线
    ElMessage.success('路线优化成功')
    
    // TODO: 在地图上绘制优化后的路线
  } catch (error) {
    ElMessage.error('路线优化失败')
  } finally {
    optimizing.value = false
  }
}

// 保存行程
const saveTrip = () => {
  tripForm.value.destination = searchForm.value.city
  tripForm.value.title = `${searchForm.value.city}${tripForm.value.days}日游`
  saveTripDialogVisible.value = true
}

// 确认保存行程
const confirmSaveTrip = async () => {
  if (!tripForm.value.title || !tripForm.value.destination) {
    ElMessage.warning('请填写完整信息')
    return
  }

  saving.value = true
  try {
    const tripData = {
      ...tripForm.value,
      attractions: selectedAttractions.value.map(a => ({
        name: a.name,
        lng: a.lng,
        lat: a.lat,
        type: a.type,
        address: a.address,
        rating: a.rating,
        cost: a.cost
      }))
    }

    const result = await createTrip(tripData, true)
    ElMessage.success('行程保存成功')
    saveTripDialogVisible.value = false
    
    // 跳转到行程详情
    router.push(`/trips/${(result as any).id}`)
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  nextTick(() => {
    initMap()
  })
})
</script>

<style scoped>
.map-view {
  height: calc(100vh - 100px);
}

.sidebar {
  height: 100%;
  overflow-y: auto;
}

.selected-section {
  margin: 20px 0;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.attraction-tag {
  margin: 5px;
}

.attractions-list {
  margin-top: 20px;
}

.attraction-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.attraction-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.attraction-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  flex-shrink: 0;
}

.image-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  flex-shrink: 0;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

.attraction-info {
  flex: 1;
  min-width: 0;
}

.attraction-info h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attraction-info .address {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.map-container {
  height: 100%;
}
</style>

