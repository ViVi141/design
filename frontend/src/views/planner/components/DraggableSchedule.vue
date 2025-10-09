<template>
  <div class="draggable-schedule">
    <!-- 待安排区域（参考携程） -->
    <el-card class="pending-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📦 待安排</span>
          <el-badge :value="pendingItems.length" v-if="pendingItems.length > 0" />
        </div>
      </template>
      
      <div class="pending-items">
        <el-empty v-if="pendingItems.length === 0" :image-size="80" description="暂无待安排项目" />
        
        <div
          v-for="item in pendingItems"
          :key="item.id"
          class="pending-item"
          draggable="true"
          @dragstart="onDragStart(item, $event)"
        >
          <div class="item-icon">
            <el-icon><MapLocation /></el-icon>
          </div>
          <div class="item-info">
            <h4>{{ item.name }}</h4>
            <p>{{ item.address }}</p>
          </div>
          <el-button
            size="small"
            type="primary"
            @click="scheduleItem(item)"
          >
            安排
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 日程安排区域 -->
    <div class="schedule-area">
      <div
        v-for="day in days"
        :key="day"
        class="day-card"
        @drop="onDrop(day, $event)"
        @dragover.prevent
        @dragenter="onDragEnter(day)"
        @dragleave="onDragLeave"
      >
        <div class="day-header">
          <span class="day-title">第 {{ day }} 天</span>
          <span class="day-stats">{{ getDayItemsCount(day) }}项</span>
        </div>

        <div class="day-items">
          <el-empty
            v-if="getDayItems(day).length === 0"
            :image-size="60"
            description="拖拽项目到这里或点击添加"
          >
            <el-button size="small" @click="$emit('add-item', day)">+ 添加</el-button>
          </el-empty>

          <div
            v-for="(item, index) in getDayItems(day)"
            :key="item.id"
            class="schedule-item"
            draggable="true"
            @dragstart="onDragStart(item, $event)"
          >
            <div class="item-drag-handle">
              <el-icon><Rank /></el-icon>
            </div>
            
            <div class="item-index">{{ index + 1 }}</div>
            
            <div class="item-type-icon">
              <el-icon v-if="item.type === 'attraction'" color="#409eff"><MapLocation /></el-icon>
              <el-icon v-else-if="item.type === 'hotel'" color="#67c23a"><House /></el-icon>
              <el-icon v-else-if="item.type === 'transport'" color="#e6a23c"><Van /></el-icon>
              <el-icon v-else color="#909399"><Memo /></el-icon>
            </div>

            <div class="item-content">
              <h4>{{ item.name }}</h4>
              <p v-if="item.description">{{ item.description }}</p>
              
              <div class="item-tags">
                <el-tag size="small" v-if="item.time">⏰ {{ item.time }}</el-tag>
                <el-tag size="small" type="success" v-if="item.cost">{{ item.cost }}</el-tag>
                <el-tag size="small" type="info" v-if="item.duration">{{ item.duration }}</el-tag>
              </div>

              <!-- 备注区域（参考携程） -->
              <div v-if="item.note || showNoteInput === item.id" class="item-note">
                <el-input
                  v-if="showNoteInput === item.id"
                  v-model="item.note"
                  placeholder="添加备注..."
                  @blur="showNoteInput = null"
                  autosize
                  type="textarea"
                />
                <div v-else class="note-display" @click="showNoteInput = item.id">
                  <el-icon><Edit /></el-icon>
                  {{ item.note || '点击添加备注' }}
                </div>
              </div>
            </div>

            <div class="item-actions">
              <el-button-group size="small">
                <el-button :icon="'Edit'" @click="showNoteInput = item.id" circle />
                <el-button type="danger" :icon="'Delete'" @click="$emit('remove-item', item.id)" circle />
              </el-button-group>
            </div>
          </div>
        </div>

        <div class="day-footer">
          <el-button text type="primary" size="small" @click="$emit('add-item', day)">
            <el-icon><Plus /></el-icon>
            添加项目
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MapLocation, House, Van, Memo, Rank, Edit, Plus } from '@element-plus/icons-vue'

interface ScheduleItem {
  id: string
  day?: number
  type: string
  name: string
  description?: string
  address?: string
  time?: string
  duration?: string
  cost?: string
  note?: string
  data?: any
}

const props = defineProps<{
  items: ScheduleItem[]
  days: number
}>()

const emit = defineEmits(['update:items', 'add-item', 'remove-item'])

const showNoteInput = ref<string | null>(null)
const draggedItem = ref<ScheduleItem | null>(null)
const dragOverDay = ref<number | null>(null)

// 待安排的项目（day为undefined或0）
const pendingItems = computed(() => {
  return props.items.filter(item => !item.day || item.day === 0)
})

// 获取指定天的项目
const getDayItems = (day: number) => {
  return props.items.filter(item => item.day === day)
}

// 获取指定天的项目数量
const getDayItemsCount = (day: number) => {
  return getDayItems(day).length
}

// 拖拽开始
const onDragStart = (item: ScheduleItem, event: DragEvent) => {
  draggedItem.value = item
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', item.id)
  }
}

// 拖拽进入
const onDragEnter = (day: number) => {
  dragOverDay.value = day
}

// 拖拽离开
const onDragLeave = () => {
  dragOverDay.value = null
}

// 放置
const onDrop = (day: number, event: DragEvent) => {
  event.preventDefault()
  
  if (!draggedItem.value) return

  // 更新项目的day属性
  const updatedItems = props.items.map(item => {
    if (item.id === draggedItem.value!.id) {
      return { ...item, day }
    }
    return item
  })

  emit('update:items', updatedItems)
  draggedItem.value = null
  dragOverDay.value = null
}

// 安排项目到指定天
const scheduleItem = (item: ScheduleItem) => {
  const updatedItems = props.items.map(i => {
    if (i.id === item.id) {
      return { ...i, day: 1 }
    }
    return i
  })
  emit('update:items', updatedItems)
}
</script>

<style scoped>
.draggable-schedule {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 待安排卡片（参考携程） */
.pending-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pending-items {
  max-height: 300px;
  overflow-y: auto;
}

.pending-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  cursor: move;
  transition: all 0.3s;
}

.pending-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

/* 日程卡片 */
.schedule-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.day-card {
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  background: white;
  transition: all 0.3s;
}

.day-card[data-drag-over] {
  border-color: #409eff;
  background: #ecf5ff;
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
}

.day-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.day-stats {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 4px 12px;
  border-radius: 12px;
}

.day-items {
  min-height: 100px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: #f9fafc;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  cursor: move;
  transition: all 0.3s;
}

.schedule-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.item-drag-handle {
  color: #c0c4cc;
  cursor: move;
}

.item-drag-handle:hover {
  color: #409eff;
}

.item-index {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.item-type-icon {
  font-size: 24px;
}

.item-icon {
  font-size: 24px;
  color: #409eff;
}

.item-info,
.item-content {
  flex: 1;
  min-width: 0;
}

.item-info h4,
.item-content h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
}

.item-info p,
.item-content p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #606266;
}

.item-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

/* 备注区域（参考携程） */
.item-note {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e4e7ed;
}

.note-display {
  padding: 8px;
  background: #fff;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.note-display:hover {
  border-color: #409eff;
  color: #409eff;
}

.day-footer {
  margin-top: 12px;
  text-align: center;
  padding-top: 12px;
  border-top: 1px dashed #e4e7ed;
}
</style>

