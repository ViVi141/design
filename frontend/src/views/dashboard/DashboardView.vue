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
              <el-button text @click="goToTrips">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentTrips" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="destination" label="目的地" width="120" />
            <el-table-column prop="days" label="天数" width="80" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, MapLocation, Location, MagicStick, DataAnalysis } from '@element-plus/icons-vue'
import { getTrips } from '@/api/trip'

const router = useRouter()

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

const loadRecentTrips = async () => {
  try {
    const data = await getTrips({ limit: 5 })
    recentTrips.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载行程失败:', error)
  }
}

const goToChat = () => {
  router.push('/planner')  // 改为智能规划器
}

const goToMap = () => {
  router.push('/planner')  // 改为智能规划器
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
</style>

