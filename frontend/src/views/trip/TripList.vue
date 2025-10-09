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

      <!-- 搜索和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="目的地">
          <el-input v-model="searchForm.destination" placeholder="搜索目的地" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px;">
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
          </el-select>
        </el-form-item>
        <el-form-item label="天数">
          <el-input-number v-model="searchForm.minDays" :min="1" :max="30" placeholder="最少" style="width: 100px;" />
          <span style="margin: 0 5px;">-</span>
          <el-input-number v-model="searchForm.maxDays" :min="1" :max="30" placeholder="最多" style="width: 100px;" />
        </el-form-item>
        <el-form-item label="排序">
          <el-select v-model="searchForm.sortBy" placeholder="排序方式" style="width: 150px;">
            <el-option label="最新创建" value="created_desc" />
            <el-option label="最早创建" value="created_asc" />
            <el-option label="目的地A-Z" value="destination_asc" />
            <el-option label="目的地Z-A" value="destination_desc" />
            <el-option label="天数升序" value="days_asc" />
            <el-option label="天数降序" value="days_desc" />
            <el-option label="预算升序" value="budget_asc" />
            <el-option label="预算降序" value="budget_desc" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTrips">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
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
import { Plus, Search, RefreshLeft } from '@element-plus/icons-vue'
import { getTrips, deleteTrip as deleteTripApi, optimizeTrip as optimizeTripApi, type Trip } from '@/api/trip'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const trips = ref<Trip[]>([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = ref({
  destination: '',
  status: '',
  minDays: undefined as number | undefined,
  maxDays: undefined as number | undefined,
  sortBy: 'created_desc'
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
    let filteredTrips = (data as Trip[]) || []
    
    // 前端筛选（如果后端不支持）
    if (searchForm.value.status) {
      filteredTrips = filteredTrips.filter(trip => trip.status === searchForm.value.status)
    }
    
    if (searchForm.value.minDays !== undefined) {
      filteredTrips = filteredTrips.filter(trip => trip.days >= (searchForm.value.minDays || 0))
    }
    
    if (searchForm.value.maxDays !== undefined) {
      filteredTrips = filteredTrips.filter(trip => trip.days <= (searchForm.value.maxDays || 999))
    }
    
    // 排序
    filteredTrips = sortTrips(filteredTrips, searchForm.value.sortBy)
    
    trips.value = filteredTrips
    total.value = filteredTrips.length
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 排序函数
const sortTrips = (tripList: Trip[], sortBy: string) => {
  const sorted = [...tripList]
  
  switch (sortBy) {
    case 'created_desc':
      return sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    case 'created_asc':
      return sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    case 'destination_asc':
      return sorted.sort((a, b) => (a.destination || '').localeCompare(b.destination || '', 'zh-CN'))
    case 'destination_desc':
      return sorted.sort((a, b) => (b.destination || '').localeCompare(a.destination || '', 'zh-CN'))
    case 'days_asc':
      return sorted.sort((a, b) => (a.days || 0) - (b.days || 0))
    case 'days_desc':
      return sorted.sort((a, b) => (b.days || 0) - (a.days || 0))
    case 'budget_asc':
      return sorted.sort((a, b) => (a.budget || 0) - (b.budget || 0))
    case 'budget_desc':
      return sorted.sort((a, b) => (b.budget || 0) - (a.budget || 0))
    default:
      return sorted
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    destination: '',
    status: '',
    minDays: undefined,
    maxDays: undefined,
    sortBy: 'created_desc'
  }
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

// 前往智能规划
const goToMap = () => {
  router.push('/ultimate-planner')
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

.search-form .el-form-item {
  margin-bottom: 10px;
}

:deep(.el-input-number) {
  width: 100px;
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

