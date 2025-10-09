<template>
  <div class="trip-list">
    <el-card>
      <template #header>
        <div class="header">
          <span>我的行程</span>
          <el-button type="primary" @click="goToMap">
            <el-icon><Plus /></el-icon>
            创建新行程
          </el-button>
        </div>
      </template>

      <!-- 搜索 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="目的地">
          <el-input v-model="searchForm.destination" placeholder="搜索目的地" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTrips">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 行程列表 -->
      <el-table :data="trips" style="width: 100%" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="trip-detail">
              <h4>景点列表：</h4>
              <el-tag
                v-for="(attraction, index) in row.attractions"
                :key="index"
                style="margin: 5px"
              >
                {{ attraction.name }}
              </el-tag>
              
              <div v-if="row.summary" class="summary-info">
                <h4>行程统计：</h4>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="景点数量">
                    {{ row.summary.num_attractions }} 个
                  </el-descriptions-item>
                  <el-descriptions-item label="总距离">
                    {{ row.summary.total_distance_km }} km
                  </el-descriptions-item>
                  <el-descriptions-item label="总时间">
                    {{ row.summary.total_duration_hours }} 小时
                  </el-descriptions-item>
                  <el-descriptions-item label="总费用">
                    ¥{{ row.summary.total_cost }}
                  </el-descriptions-item>
                  <el-descriptions-item label="优化率" v-if="row.summary.optimization_rate">
                    {{ row.summary.optimization_rate.toFixed(1) }}%
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="destination" label="目的地" width="120" />
        <el-table-column prop="days" label="天数" width="80">
          <template #default="{ row }">
            {{ row.days }} 天
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="预算" width="120">
          <template #default="{ row }">
            {{ row.budget ? `¥${row.budget}` : '-' }}
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewTrip(row.id)">查看</el-button>
            <el-button link type="warning" @click="optimizeTrip(row.id)">优化</el-button>
            <el-button link type="danger" @click="deleteTrip(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadTrips"
        @current-change="loadTrips"
        style="margin-top: 20px; justify-content: center"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getTrips, deleteTrip as deleteTripApi, optimizeTrip as optimizeTripApi, type Trip } from '@/api/trip'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const trips = ref<Trip[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = ref({
  destination: ''
})

// 加载行程列表
const loadTrips = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params: any = {
      skip,
      limit: pageSize.value
    }
    
    if (searchForm.value.destination) {
      params.destination = searchForm.value.destination
    }

    const data = await getTrips(params)
    trips.value = data as Trip[]
    total.value = trips.value.length // 注意：实际项目中应该从后端返回总数
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value.destination = ''
  currentPage.value = 1
  loadTrips()
}

// 查看行程
const viewTrip = (id: number) => {
  router.push(`/trips/${id}`)
}

// 优化行程
const optimizeTrip = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认要重新优化此行程的路线吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    await optimizeTripApi(id)
    ElMessage.success('优化成功')
    loadTrips()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '优化失败')
    }
  } finally {
    loading.value = false
  }
}

// 删除行程
const deleteTrip = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认要删除此行程吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    await deleteTripApi(id)
    ElMessage.success('删除成功')
    loadTrips()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  } finally {
    loading.value = false
  }
}

// 前往地图
const goToMap = () => {
  router.push('/map')
}

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

onMounted(() => {
  loadTrips()
})
</script>

<style scoped>
.trip-list {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.trip-detail {
  padding: 20px;
  background: #f5f7fa;
}

.trip-detail h4 {
  margin: 0 0 10px 0;
}

.summary-info {
  margin-top: 20px;
}
</style>

