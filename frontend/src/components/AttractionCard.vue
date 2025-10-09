<template>
  <el-card class="attraction-card" shadow="hover" :body-style="{ padding: '0' }">
    <!-- 景点图片（参考携程） -->
    <div class="card-image">
      <el-image
        v-if="attraction.photos && attraction.photos.length > 0"
        :src="attraction.photos[0]"
        fit="cover"
        :preview-src-list="attraction.photos"
        lazy
      >
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div v-else class="image-placeholder">
        <el-icon size="50"><Picture /></el-icon>
      </div>

      <!-- 评分标签（左上角） -->
      <div v-if="attraction.rating && attraction.rating > 0" class="rating-badge">
        ⭐ {{ attraction.rating.toFixed(1) }}
      </div>

      <!-- 价格标签（右上角） -->
      <div v-if="attraction.cost && attraction.cost !== '未知'" class="cost-badge">
        {{ attraction.cost }}
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <h3 class="attraction-name">{{ attraction.name }}</h3>
      
      <div class="attraction-info">
        <el-icon><Location /></el-icon>
        <span class="address">{{ attraction.address || '暂无地址' }}</span>
      </div>

      <div class="attraction-tags">
        <el-tag size="small" v-if="attraction.type" type="info">
          {{ attraction.type }}
        </el-tag>
        <el-tag size="small" v-if="attraction.tel" type="warning">
          <el-icon><Phone /></el-icon>
          {{ attraction.tel }}
        </el-tag>
      </div>

      <!-- 操作按钮 -->
      <div class="card-actions">
        <el-button 
          :type="selected ? 'success' : 'primary'" 
          size="default"
          @click="handleSelect"
          style="width: 100%"
        >
          <el-icon v-if="selected"><Check /></el-icon>
          <el-icon v-else><Plus /></el-icon>
          {{ selected ? '已选择' : '选择此景点' }}
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Picture, Location, Phone, Check, Plus } from '@element-plus/icons-vue'

interface Attraction {
  id: string
  name: string
  address?: string
  type?: string
  rating?: number
  cost?: string
  tel?: string
  photos?: string[]
}

const props = defineProps<{
  attraction: Attraction
  selected?: boolean
}>()

const emit = defineEmits(['select', 'deselect'])

const handleSelect = () => {
  if (props.selected) {
    emit('deselect', props.attraction)
  } else {
    emit('select', props.attraction)
  }
}
</script>

<style scoped>
.attraction-card {
  height: 100%;
  transition: all 0.3s;
  cursor: pointer;
}

.attraction-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 图片区域 */
.card-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.card-image :deep(.el-image),
.image-placeholder,
.image-error {
  width: 100%;
  height: 100%;
}

.image-placeholder,
.image-error {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
}

/* 评分标签 */
.rating-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  color: #f59e0b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 价格标签 */
.cost-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(67, 196, 35, 0.95);
  backdrop-filter: blur(10px);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: bold;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 卡片内容 */
.card-content {
  padding: 16px;
}

.attraction-name {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.attraction-info {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 12px;
  color: #606266;
  font-size: 13px;
}

.address {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.attraction-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.card-actions {
  margin-top: 12px;
}
</style>

