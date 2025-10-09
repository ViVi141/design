<template>
  <div class="trip-detail">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">{{ trip?.title }}</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px" v-loading="loading">
      <!-- 左侧：行程信息 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border v-if="trip">
            <el-descriptions-item label="标题">{{ trip.title }}</el-descriptions-item>
            <el-descriptions-item label="目的地">{{ trip.destination }}</el-descriptions-item>
            <el-descriptions-item label="天数">{{ trip.days }} 天</el-descriptions-item>
            <el-descriptions-item label="预算">
              {{ trip.budget ? `¥${trip.budget}` : '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="trip.status === 'confirmed' ? 'success' : 'info'">
                {{ trip.status === 'confirmed' ? '已确认' : '草稿' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(trip.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px" v-if="trip?.summary">
          <template #header>
            <span>行程统计</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="景点数量">
              {{ trip.summary.num_attractions }} 个
            </el-descriptions-item>
            <el-descriptions-item label="总距离">
              {{ trip.summary.total_distance_km }} km
            </el-descriptions-item>
            <el-descriptions-item label="总时间">
              {{ trip.summary.total_duration_hours }} 小时
            </el-descriptions-item>
            <el-descriptions-item label="总费用">
              ¥{{ trip.summary.total_cost }}
            </el-descriptions-item>
            <el-descriptions-item label="优化率" v-if="trip.summary.optimization_rate">
              <el-tag type="success">{{ trip.summary.optimization_rate.toFixed(1) }}%</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card style="margin-top: 20px">
          <template #header>
            <span>操作</span>
          </template>
          <div class="actions">
            <el-button type="primary" @click="confirmTrip" v-if="trip?.status === 'draft'">
              <el-icon><Check /></el-icon>
              确认行程
            </el-button>
            <el-button @click="optimizeRoute">
              <el-icon><MagicStick /></el-icon>
              重新优化
            </el-button>
            <el-button @click="exportTrip">
              <el-icon><Download /></el-icon>
              导出JSON
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：景点列表和路线 -->
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>景点列表</span>
          </template>
          <el-timeline v-if="trip?.attractions && trip.attractions.length > 0">
            <el-timeline-item
              v-for="(attraction, index) in trip.attractions"
              :key="index"
              :timestamp="`第 ${index + 1} 站`"
              placement="top"
            >
              <el-card shadow="hover">
                <h4>{{ attraction.name }}</h4>
                <p>{{ attraction.address }}</p>
                <div class="meta">
                  <el-tag size="small" v-if="attraction.rating">⭐ {{ attraction.rating }}</el-tag>
                  <el-tag size="small" type="success" v-if="attraction.cost">
                    {{ attraction.cost }}
                  </el-tag>
                </div>
                <div v-if="getRouteInfo(index)" class="route-info">
                  <el-divider />
                  <p style="font-size: 12px; color: #909399">
                    <el-icon><Position /></el-icon>
                    距离下一站：{{ getRouteInfo(index).distance }} m，
                    步行约 {{ getRouteInfo(index).duration }} 分钟
                  </p>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无景点" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, MagicStick, Download, Position } from '@element-plus/icons-vue'
import { getTrip, updateTrip, optimizeTrip as optimizeTripApi, type Trip } from '@/api/trip'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const trip = ref<Trip | null>(null)

// 加载行程详情
const loadTrip = async () => {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const data = await getTrip(id)
    trip.value = data as Trip
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 确认行程
const confirmTrip = async () => {
  if (!trip.value) return

  try {
    await updateTrip(trip.value.id, { status: 'confirmed' } as any)
    ElMessage.success('行程已确认')
    loadTrip()
  } catch (error) {
    ElMessage.error('确认失败')
  }
}

// 优化路线
const optimizeRoute = async () => {
  if (!trip.value) return

  try {
    await ElMessageBox.confirm('确认要重新优化路线吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    await optimizeTripApi(trip.value.id)
    ElMessage.success('优化成功')
    loadTrip()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '优化失败')
    }
  } finally {
    loading.value = false
  }
}

// 导出行程
const exportTrip = () => {
  if (!trip.value) return

  const dataStr = JSON.stringify(trip.value, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `trip_${trip.value.id}_${trip.value.destination}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
  
  ElMessage.success('导出成功')
}

// 获取路线信息
const getRouteInfo = (index: number) => {
  if (!trip.value?.routes || index >= trip.value.routes.length) {
    return null
  }
  
  const route = trip.value.routes[index]
  return {
    distance: Math.round(route.distance),
    duration: Math.round(route.duration / 60)
  }
}

// 返回
const goBack = () => {
  router.push('/trips')
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadTrip()
})
</script>

<style scoped>
.trip-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.meta {
  display: flex;
  gap: 5px;
  margin-top: 10px;
}

.route-info {
  margin-top: 10px;
}
</style>

