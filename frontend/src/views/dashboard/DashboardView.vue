<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <h1>🎉 欢迎使用智能旅行规划系统</h1>
          <p>基于GIS与AI的智能旅行规划系统，让您的旅行更加智能、便捷</p>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="goToChat">
              <el-icon><ChatDotRound /></el-icon>
              开始AI规划
            </el-button>
            <el-button size="large" @click="goToMap">
              <el-icon><MapLocation /></el-icon>
              地图浏览
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 统计概览 -->
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="总行程数" :value="stats.totalTrips">
            <template #prefix>
              <el-icon color="#409EFF"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="已确认行程" :value="stats.confirmedTrips">
            <template #prefix>
              <el-icon color="#67C23A"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="总天数" :value="stats.totalDays">
            <template #prefix>
              <el-icon color="#E6A23C"><Calendar /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <el-statistic title="访问景点" :value="stats.totalAttractions">
            <template #prefix>
              <el-icon color="#F56C6C"><Location /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <!-- 功能介绍 -->
      <el-col :xs="24" :sm="12" :md="6" v-for="feature in features" :key="feature.title">
        <el-card class="feature-card" shadow="hover">
          <div class="feature-icon">
            <el-icon :size="40"><component :is="feature.icon" /></el-icon>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </el-card>
      </el-col>

      <!-- 最近行程 -->
      <el-col :span="24" v-if="recentTrips.length > 0">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近行程</span>
              <div class="header-actions">
                <el-select v-model="sortBy" placeholder="排序方式" size="small" @change="loadRecentTrips" style="width: 140px; margin-right: 10px;">
                  <el-option label="最新创建" value="created_desc" />
                  <el-option label="最早创建" value="created_asc" />
                  <el-option label="目的地A-Z" value="destination_asc" />
                  <el-option label="天数升序" value="days_asc" />
                  <el-option label="天数降序" value="days_desc" />
                </el-select>
                <el-button text @click="goToTrips">查看全部</el-button>
              </div>
            </div>
          </template>
          <el-table :data="displayTrips" style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="destination" label="目的地" width="120" />
            <el-table-column prop="days" label="天数" width="80">
              <template #default="{ row }">
                {{ row.days }} 天
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'confirmed' ? 'success' : 'info'" size="small">
                  {{ row.status === 'confirmed' ? '已确认' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewTrip(row.id)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, MapLocation, Location, MagicStick, DataAnalysis, Document, CircleCheck, Calendar } from '@element-plus/icons-vue'
import { getTrips } from '@/api/trip'

const router = useRouter()

// 统计数据
const stats = computed(() => {
  return {
    totalTrips: recentTrips.value.length,
    confirmedTrips: recentTrips.value.filter(t => t.status === 'confirmed').length,
    totalDays: recentTrips.value.reduce((sum, t) => sum + (t.days || 0), 0),
    totalAttractions: recentTrips.value.reduce((sum, t) => sum + (t.attractions?.length || 0), 0)
  }
})

// 监听排序变化
watch(sortBy, () => {
  sortTrips()
})

const features = [
  {
    icon: ChatDotRound,
    title: 'AI智能对话',
    description: '通过自然语言描述需求，AI自动生成旅行计划'
  },
  {
    icon: Location,
    title: '地图可视化',
    description: '直观展示景点位置、路线规划、行程安排'
  },
  {
    icon: MagicStick,
    title: '智能路径优化',
    description: '基于TSP算法优化景点访问顺序，减少路程'
  },
  {
    icon: DataAnalysis,
    title: '数据分析',
    description: '图表展示行程统计，费用分析一目了然'
  }
]

const recentTrips = ref<any[]>([])
const sortBy = ref('created_desc')
const displayTrips = ref<any[]>([])

const loadRecentTrips = async () => {
  try {
    const data = await getTrips({ limit: 10 })
    recentTrips.value = Array.isArray(data) ? data : []
    sortTrips()
  } catch (error) {
    console.error('加载行程失败:', error)
  }
}

// 排序行程
const sortTrips = () => {
  let sorted = [...recentTrips.value]
  
  switch (sortBy.value) {
    case 'created_desc':
      sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      break
    case 'created_asc':
      sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
      break
    case 'destination_asc':
      sorted.sort((a, b) => (a.destination || '').localeCompare(b.destination || '', 'zh-CN'))
      break
    case 'days_asc':
      sorted.sort((a, b) => (a.days || 0) - (b.days || 0))
      break
    case 'days_desc':
      sorted.sort((a, b) => (b.days || 0) - (a.days || 0))
      break
  }
  
  displayTrips.value = sorted.slice(0, 5)
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

const goToChat = () => {
  router.push('/ultimate-planner')
}

const goToMap = () => {
  router.push('/map')
}

const goToTrips = () => {
  router.push('/trips')
}

const viewTrip = (id: number) => {
  router.push(`/trips/${id}`)
}

onMounted(() => {
  loadRecentTrips()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-card h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
}

.welcome-card p {
  margin: 0 0 30px 0;
  font-size: 18px;
  opacity: 0.9;
}

.quick-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.feature-card {
  text-align: center;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.feature-card h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.feature-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.stat-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
}

:deep(.el-statistic__number) {
  font-size: 24px;
  font-weight: bold;
}
</style>

