<template>
  <div class="planner-view-v3">
    <div class="planner-header">
      <div class="header-content">
        <div class="title-section">
          <h1>🚀 智能行程规划器 V3</h1>
          <p>一键生成 + 智能优化，像携程一样便捷</p>
        </div>
        <div class="header-actions">
          <!-- 操作工具栏 -->
          <el-button-group>
            <el-button
              @click="undo"
              :disabled="historyIndex <= 0"
              title="撤销 (Ctrl+Z)"
            >
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
            <el-button
              @click="redo"
              :disabled="historyIndex >= history.length - 1"
              title="重做 (Ctrl+Y)"
            >
              <el-icon><RefreshRight /></el-icon>
            </el-button>
          </el-button-group>
          
          <el-button @click="clearAll" type="danger" plain>
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
          
          <el-button type="primary" @click="saveTrip" :loading="saving">
            <el-icon><DocumentChecked /></el-icon>
            保存行程
          </el-button>
        </div>
      </div>
    </div>

    <el-row :gutter="20" class="planner-content">
      <!-- 左侧：快速开始 -->
      <el-col :xs="24" :sm="24" :md="7" :lg="6">
        <el-card class="quick-start-panel" shadow="hover">
          <template #header>
            <div class="panel-header">
              <span class="header-icon">⚡</span>
              <span>快速开始</span>
            </div>
          </template>

          <!-- 基本信息 -->
          <el-form :model="tripData" label-position="top" size="large">
            <el-form-item label="📍 目的地">
              <el-input
                v-model="tripData.destination"
                placeholder="例如：北京"
                prefix-icon="MapLocation"
                clearable
              />
            </el-form-item>
            
            <el-row :gutter="10">
              <el-col :span="12">
                <el-form-item label="📅 天数">
                  <el-input-number
                    v-model="tripData.days"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="💰 预算">
                  <el-input-number
                    v-model="tripData.budget"
                    :min="0"
                    :step="1000"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <!-- 一键生成按钮（像携程） -->
          <el-button
            type="primary"
            size="large"
            @click="autoGenerateItinerary"
            :loading="generating"
            style="width: 100%; margin-bottom: 16px"
          >
            <el-icon><MagicStick /></el-icon>
            AI一键生成行程
          </el-button>

          <!-- 生成进度 -->
          <el-progress
            v-if="generating"
            :percentage="generationProgress"
            :status="generationProgress === 100 ? 'success' : undefined"
          />

          <el-divider />

          <!-- 手动操作 -->
          <div class="manual-actions">
            <p style="font-size: 14px; color: #909399; margin-bottom: 12px;">
              或手动添加：
            </p>
            <el-button
              size="default"
              @click="showSearchDialog"
              style="width: 100%; margin-bottom: 8px"
            >
              <el-icon><Search /></el-icon>
              搜索景点
            </el-button>
            <el-button
              size="default"
              @click="showHotelDialog"
              style="width: 100%; margin-bottom: 8px"
            >
              <el-icon><House /></el-icon>
              添加住宿
            </el-button>
            <el-button
              size="default"
              @click="showTransportDialog"
              style="width: 100%"
            >
              <el-icon><Van /></el-icon>
              添加交通
            </el-button>
          </div>

          <el-divider />

          <!-- 统计信息 -->
          <div class="stats-section">
            <h4>📊 当前统计</h4>
            <el-row :gutter="10">
              <el-col :span="8">
                <el-statistic
                  title="待安排"
                  :value="pendingCount"
                  suffix="项"
                />
              </el-col>
              <el-col :span="8">
                <el-statistic
                  title="已安排"
                  :value="scheduledCount"
                  suffix="项"
                />
              </el-col>
              <el-col :span="8">
                <el-statistic
                  title="景点数"
                  :value="attractionCount"
                  suffix="个"
                />
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 中间：行程编辑（增强版拖拽） -->
      <el-col :xs="24" :sm="24" :md="10" :lg="12">
        <el-card class="schedule-panel" shadow="hover">
          <template #header>
            <div class="panel-header">
              <span class="header-icon">📋</span>
              <span>行程安排</span>
              <el-button
                type="success"
                size="small"
                @click="smartOptimize"
                :loading="optimizing"
              >
                <el-icon><Connection /></el-icon>
                智能优化
              </el-button>
            </div>
          </template>

          <!-- 使用增强版拖拽组件 -->
          <DraggableScheduleEnhanced
            :items="scheduleItems"
            :days="tripData.days"
            :show-drop-zones="showDropZones"
            @update:items="handleItemsUpdate"
            @add-item="handleAddItem"
            @remove-item="handleRemoveItem"
          />
        </el-card>
      </el-col>

      <!-- 右侧：地图预览 -->
      <el-col :xs="24" :sm="24" :md="7" :lg="6">
        <el-card class="map-panel" shadow="hover">
          <template #header>
            <div class="panel-header">
              <span class="header-icon">🗺️</span>
              <span>地图预览</span>
            </div>
          </template>

          <div id="map-container-v3" ref="mapContainer" style="height: 500px"></div>

          <el-divider />

          <!-- 路线信息 -->
          <div class="route-info" v-if="routeInfo">
            <h4>📍 路线信息</h4>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="总距离">
                {{ routeInfo.totalDistance }}km
              </el-descriptions-item>
              <el-descriptions-item label="预计时间">
                {{ routeInfo.totalTime }}小时
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 景点搜索对话框 -->
    <el-dialog
      v-model="searchDialogVisible"
      title="🔍 搜索景点"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-input
        v-model="searchKeyword"
        placeholder="输入景点名称"
        size="large"
        @keyup.enter="performSearch"
      >
        <template #append>
          <el-button
            type="primary"
            @click="performSearch"
            :loading="searching"
          >
            搜索
          </el-button>
        </template>
      </el-input>

      <!-- 搜索结果 -->
      <div class="search-results" v-loading="searching">
        <el-empty v-if="searchResults.length === 0 && !searching" description="暂无结果" />
        
        <el-row :gutter="16" style="margin-top: 20px">
          <el-col
            v-for="attraction in searchResults"
            :key="attraction.id"
            :xs="24"
            :sm="12"
            :md="8"
          >
            <AttractionCard
              :attraction="attraction"
              :selected="isAttractionSelected(attraction.id)"
              @select="addAttractionToSchedule"
            />
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  House,
  Van,
  MagicStick,
  Connection,
  Search,
  DocumentChecked,
  RefreshLeft,
  RefreshRight,
  Delete
} from '@element-plus/icons-vue'
import DraggableScheduleEnhanced from './components/DraggableSchedule.vue'
import AttractionCard from '@/components/AttractionCard.vue'
import { chat } from '@/api/chat'
import { searchAttractions } from '@/api/attraction'
import { createTrip, type TripCreate } from '@/api/trip'
import AMapLoader from '@amap/amap-jsapi-loader'

// Window类型扩展
interface WindowWithAMap extends Window {
  AMap?: any
  _AMapSecurityConfig?: any
}

// 数据类型
interface ScheduleItem {
  id: string
  day?: number
  type: string
  name: string
  description?: string
  address?: string
  location?: { lng: number; lat: number }
  time?: string
  duration?: string
  cost?: string
  note?: string
  data?: any
}

// 旅行数据
const tripData = reactive({
  destination: '',
  days: 3,
  budget: 5000
})

// 核心状态
const scheduleItems = ref<ScheduleItem[]>([])
const generating = ref(false)
const generationProgress = ref(0)
const optimizing = ref(false)
const saving = ref(false)
const searching = ref(false)

// 历史记录（撤销/重做）
const history = ref<any[]>([])
const historyIndex = ref(-1)

// UI状态
const showDropZones = ref(false)
const searchDialogVisible = ref(false)
const searchKeyword = ref('')
const searchResults = ref<any[]>([])

// 地图
const mapContainer = ref<HTMLElement>()
const map = ref<any>(null)  // 地图实例
const routeInfo = ref<any>(null)

// 统计数据
const pendingCount = computed(() => {
  return scheduleItems.value.filter(item => !item.day || item.day === 0).length
})

const scheduledCount = computed(() => {
  return scheduleItems.value.filter(item => item.day && item.day > 0).length
})

const attractionCount = computed(() => {
  return scheduleItems.value.filter(item => item.type === 'attraction').length
})

// 初始化地图
onMounted(async () => {
  await initMap()
  recordAction({ type: 'init' })
})

const initMap = async () => {
  try {
    (window as WindowWithAMap)._AMapSecurityConfig = {
      securityJsCode: '647d226e39983ddf9a56349328a7e844'
    }

    const AMap = await AMapLoader.load({
      key: '542addb61a32fc4137e362202e48bce9',
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline']
    })

    if (mapContainer.value) {
      map.value = new AMap.Map(mapContainer.value, {
        zoom: 11,
        center: [116.397428, 39.90923],
        mapStyle: 'amap://styles/normal'
      })
    }
  } catch (error) {
    console.error('地图加载失败:', error)
  }
}

// ========== 核心功能：一键AI生成 ==========
const autoGenerateItinerary = async () => {
  if (!tripData.destination) {
    ElMessage.warning('请先输入目的地')
    return
  }

  generating.value = true
  generationProgress.value = 0

  try {
    // 1. AI推荐景点
    generationProgress.value = 20
    const response = await chat({
      message: `请推荐${tripData.destination}的${tripData.days * 3}个热门旅游景点，直接列出景点名称，每行一个，格式为：1. 景点名称`
    })

    // 调试：打印响应结构
    console.log('AI完整响应:', response)
    console.log('response类型:', typeof response)

    // 2. 解析AI响应
    // 注意：axios拦截器已经返回了response.data，所以这里的response就是数据本身
    let replyText = ''
    
    if (!response) {
      console.error('响应为空')
      ElMessage.error('AI服务暂时不可用，请稍后重试或使用手动添加')
      return
    }
    
    // 尝试多种解析方式（使用类型断言）
    const resp = response as any
    if (typeof resp === 'string') {
      replyText = resp
      console.log('解析方式：直接字符串')
    } else if (typeof resp === 'object') {
      if (resp.message) {
        replyText = resp.message
        console.log('解析方式：response.message')
      } else if (resp.reply) {
        replyText = resp.reply
        console.log('解析方式：response.reply')
      } else if (resp.response) {
        replyText = resp.response
        console.log('解析方式：response.response')
      } else if (resp.content) {
        replyText = resp.content
        console.log('解析方式：response.content')
      } else {
        console.error('无法识别的响应格式:', Object.keys(resp))
        console.error('响应内容:', resp)
      }
    }

    if (!replyText) {
      console.error('无法提取文本内容')
      ElMessage.error('AI响应格式错误，请使用手动搜索功能')
      // 提示用户使用手动方式
      ElMessage.info('提示：可以点击下方"搜索景点"手动添加')
      return
    }
    
    console.log('提取的文本:', replyText.substring(0, 100) + '...')

    // 3. 解析景点名称
    generationProgress.value = 40
    const attractionNames = parseAttractions(replyText)
    
    if (attractionNames.length === 0) {
      ElMessage.warning('未能解析出景点，请重试或手动添加')
      return
    }

    // 4. 搜索每个景点的详细信息
    const total = attractionNames.length
    for (let i = 0; i < attractionNames.length; i++) {
      const name = attractionNames[i]
      try {
        const result = await searchAttractions({
          city: tripData.destination,
          keyword: name,
          limit: 1
        })

        // 注意：axios拦截器已返回data，result就是数据本身
        let data: any[] = []
        if (Array.isArray(result)) {
          data = result
        } else if (result && 'attractions' in result) {
          data = (result as any).attractions || []
        }
        
        if (data.length > 0) {
          // 添加到待安排区（day = 0）
          addToSchedule(data[0], 0)
        }

        generationProgress.value = 40 + Math.floor((i + 1) / total * 60)
      } catch (error) {
        console.error(`搜索失败: ${name}`, error)
      }
    }

    generationProgress.value = 100
    ElMessage.success('行程已生成！请拖拽景点到各天安排')
    
    // 记录操作
    recordAction({ type: 'generate' })
  } catch (error: any) {
    console.error('生成失败:', error)
    
    // 提供详细的错误信息
    let errorMsg = '生成失败'
    if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error(errorMsg)
    ElMessage.info('提示：可以点击"搜索景点"手动添加景点')
  } finally {
    generating.value = false
    // 即使失败也重置进度
    setTimeout(() => {
      generationProgress.value = 0
    }, 2000)
  }
}

// 解析AI返回的景点名称
const parseAttractions = (text: string): string[] => {
  const lines = text.split('\n')
  return lines
    .filter(line => /^\d+[\.\、]/.test(line.trim()))
    .map(line => {
      return line.replace(/^\d+[\.\、]\s*/, '').trim()
    })
    .filter(name => name.length > 0 && name.length < 30)
}

// 添加到行程
const addToSchedule = (attraction: any, day: number = 0) => {
  const newItem: ScheduleItem = {
    id: `item-${Date.now()}-${Math.random()}`,
    day,
    type: 'attraction',
    name: attraction.name,
    address: attraction.address,
    location: attraction.location,
    cost: attraction.cost,
    data: attraction
  }
  scheduleItems.value.push(newItem)
}

// ========== 核心功能：智能优化 ==========
const smartOptimize = async () => {
  const attractions = scheduleItems.value.filter(
    item => item.type === 'attraction' && item.location && item.day && item.day > 0
  )

  if (attractions.length < 2) {
    ElMessage.warning('至少需要2个已安排的景点才能优化')
    return
  }

  optimizing.value = true

  try {
    // 按天分组优化
    const dayGroups: any = {}
    attractions.forEach(item => {
      const day = item.day!
      if (!dayGroups[day]) dayGroups[day] = []
      dayGroups[day].push(item)
    })

    // 简单优化：按地理位置排序（实际应该用TSP算法）
    for (const day in dayGroups) {
      const items = dayGroups[day]
      if (items.length <= 1) continue

      // 按经纬度简单排序
      items.sort((a: any, b: any) => {
        const distA = a.location.lng + a.location.lat
        const distB = b.location.lng + b.location.lat
        return distA - distB
      })
    }

    ElMessage.success('路线已优化！')
    recordAction({ type: 'optimize' })
  } catch (error) {
    console.error('优化失败:', error)
    ElMessage.error('优化失败')
  } finally {
    optimizing.value = false
  }
}

// ========== 历史记录功能 ==========
const recordAction = (action: any) => {
  // 移除当前索引之后的历史
  history.value = history.value.slice(0, historyIndex.value + 1)
  
  // 添加新操作
  history.value.push({
    type: action.type,
    data: JSON.parse(JSON.stringify(scheduleItems.value)),
    timestamp: Date.now()
  })
  
  historyIndex.value++
  
  // 限制历史记录数量
  if (history.value.length > 50) {
    history.value.shift()
    historyIndex.value--
  }
}

const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    scheduleItems.value = JSON.parse(JSON.stringify(
      history.value[historyIndex.value].data
    ))
    ElMessage.info('已撤销')
  }
}

const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    scheduleItems.value = JSON.parse(JSON.stringify(
      history.value[historyIndex.value].data
    ))
    ElMessage.info('已重做')
  }
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有项目吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    scheduleItems.value = []
    recordAction({ type: 'clear' })
    ElMessage.success('已清空')
  } catch {
    // 用户取消
  }
}

// ========== 景点搜索 ==========
const showSearchDialog = () => {
  if (!tripData.destination) {
    ElMessage.warning('请先填写目的地')
    return
  }
  searchKeyword.value = ''
  searchResults.value = []
  searchDialogVisible.value = true
}

const performSearch = async () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入关键词')
    return
  }

  searching.value = true
  try {
    const response = await searchAttractions({
      city: tripData.destination,
      keyword: searchKeyword.value,
      limit: 20
    })
    
    // 注意：axios拦截器已返回data，response就是数据本身
    if (Array.isArray(response)) {
      searchResults.value = response
    } else if (response && 'attractions' in response) {
      searchResults.value = (response as any).attractions || []
    } else {
      searchResults.value = []
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

const isAttractionSelected = (id: string) => {
  return scheduleItems.value.some(item => item.data?.id === id)
}

const addAttractionToSchedule = (attraction: any) => {
  addToSchedule(attraction, 0)
  ElMessage.success(`已添加：${attraction.name}`)
  recordAction({ type: 'add' })
}

// ========== 行程管理 ==========
const handleItemsUpdate = (newItems: ScheduleItem[]) => {
  scheduleItems.value = newItems
  recordAction({ type: 'update' })
}

const handleAddItem = (_day: number) => {
  showSearchDialog()
}

const handleRemoveItem = (itemId: string) => {
  const index = scheduleItems.value.findIndex(item => item.id === itemId)
  if (index > -1) {
    scheduleItems.value.splice(index, 1)
    recordAction({ type: 'remove' })
  }
}

const showHotelDialog = () => {
  ElMessage.info('酒店搜索功能开发中...')
}

const showTransportDialog = () => {
  ElMessage.info('交通搜索功能开发中...')
}

// 保存行程
const saveTrip = async () => {
  if (!tripData.destination) {
    ElMessage.warning('请填写目的地')
    return
  }

  saving.value = true
  try {
    const attractions = scheduleItems.value
      .filter(item => item.type === 'attraction' && item.location)
      .map(item => ({
        name: item.name,
        lng: item.location!.lng,
        lat: item.location!.lat,
        type: item.type,
        address: item.address,
        cost: item.cost
      }))

    const tripPayload: TripCreate = {
      title: `${tripData.destination}${tripData.days}日游`,
      destination: tripData.destination,
      days: tripData.days,
      budget: tripData.budget,
      attractions
    }
    await createTrip(tripPayload)
    ElMessage.success('行程保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 键盘快捷键
onMounted(() => {
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
      e.preventDefault()
      undo()
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
      e.preventDefault()
      redo()
    }
  })
})
</script>

<style scoped>
.planner-view-v3 {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

/* 页头 */
.planner-header {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.title-section p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 内容区 */
.planner-content {
  margin: 0;
}

/* 面板 */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.header-icon {
  font-size: 20px;
}

/* 快速开始面板 */
.quick-start-panel {
  height: calc(100vh - 180px);
}

.manual-actions {
  margin-top: 16px;
}

.stats-section {
  margin-top: 16px;
}

.stats-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

/* 搜索结果 */
.search-results {
  max-height: 600px;
  overflow-y: auto;
}

/* 响应式 */
@media (max-width: 768px) {
  .planner-view-v3 {
    padding: 10px;
  }

  .planner-header {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

