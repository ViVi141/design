<template>
  <div class="chat-view">
    <el-row :gutter="20" style="height: 100%">
      <el-col :xs="24" :md="16" class="chat-container">
        <el-card style="height: 100%">
          <template #header>
            <div class="chat-header">
              <span>💬 AI旅行助手</span>
              <el-button text @click="clearChat">清空对话</el-button>
            </div>
          </template>

          <!-- 消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <div v-if="messages.length === 0" class="welcome-message">
              <h2>👋 你好！我是你的AI旅行助手</h2>
              <p>告诉我你的旅行需求，我会帮你规划完美的行程</p>
              <div class="example-questions">
                <p>你可以这样问我：</p>
                <el-tag @click="sendExample('我想去成都玩3天，预算5000元')">
                  我想去成都玩3天，预算5000元
                </el-tag>
                <el-tag @click="sendExample('推荐北京的历史文化景点')">
                  推荐北京的历史文化景点
                </el-tag>
                <el-tag @click="sendExample('杭州有哪些适合周末游的地方')">
                  杭州有哪些适合周末游的地方
                </el-tag>
              </div>
            </div>

            <div
              v-for="(msg, index) in messages"
              :key="index"
              :class="['message', msg.role === 'user' ? 'user-message' : 'assistant-message']"
            >
              <div class="message-avatar">
                <el-icon v-if="msg.role === 'user'"><User /></el-icon>
                <el-icon v-else><Service /></el-icon>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
              </div>
            </div>

            <div v-if="loading" class="message assistant-message">
              <div class="message-avatar">
                <el-icon><Service /></el-icon>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="input-container">
            <el-input
              v-model="inputMessage"
              :rows="3"
              type="textarea"
              placeholder="输入你的旅行需求..."
              @keydown.enter.exact="handleSend"
              :disabled="loading"
            />
            <el-button
              type="primary"
              :icon="loading ? 'Loading' : 'Position'"
              @click="handleSend"
              :loading="loading"
            >
              发送
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：需求信息 -->
      <el-col :xs="24" :md="8" class="info-panel">
        <el-card>
          <template #header>
            <span>📋 提取的需求信息</span>
          </template>

          <div v-if="requirements" class="requirements-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="目的地">
                {{ requirements.destination || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="天数">
                {{ requirements.days || '-' }} 天
              </el-descriptions-item>
              <el-descriptions-item label="预算">
                {{ requirements.budget ? `¥${requirements.budget}` : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="偏好">
                <el-tag
                  v-for="pref in requirements.preferences"
                  :key="pref"
                  size="small"
                  style="margin-right: 5px"
                >
                  {{ pref }}
                </el-tag>
                <span v-if="!requirements.preferences || requirements.preferences.length === 0">
                  -
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="出发日期">
                {{ requirements.start_date || '-' }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="actions" style="margin-top: 20px">
              <el-button type="primary" @click="goToPlan" style="width: 100%">
                <el-icon><MapLocation /></el-icon>
                开始规划行程
              </el-button>
              <el-button @click="extractFromChat" :loading="extracting" style="width: 100%; margin-top: 10px">
                <el-icon><Refresh /></el-icon>
                重新提取需求
              </el-button>
            </div>
          </div>

          <el-empty v-else description="暂无需求信息" />
        </el-card>

        <!-- 快捷操作 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>🚀 快捷操作</span>
          </template>
          <el-button @click="generateGuide" :loading="generatingGuide" style="width: 100%">
            <el-icon><Document /></el-icon>
            生成旅行攻略
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 攻略预览对话框 -->
    <el-dialog v-model="guideDialogVisible" title="旅行攻略" width="800px">
      <div v-html="guideContent" class="guide-content"></div>
      <template #footer>
        <el-button @click="guideDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="copyGuide">复制攻略</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Service, MapLocation, Refresh, Document } from '@element-plus/icons-vue'
import { chat, extractRequirements, generateGuide, type TravelRequirements } from '@/api/chat'
import dayjs from 'dayjs'

const router = useRouter()

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const loading = ref(false)
const extracting = ref(false)
const generatingGuide = ref(false)
const requirements = ref<TravelRequirements | null>(null)
const messagesContainer = ref<HTMLElement>()
const guideDialogVisible = ref(false)
const guideContent = ref('')

// 发送消息
const handleSend = async () => {
  const msg = inputMessage.value.trim()
  if (!msg || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: msg,
    timestamp: new Date()
  })
  inputMessage.value = ''

  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })

  // 调用AI
  loading.value = true
  try {
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content
    }))

    const response: any = await chat({
      message: msg,
      history
    })

    // 添加AI回复
    messages.value.push({
      role: 'assistant',
      content: response.message || response.content || '抱歉，我没有理解',
      timestamp: new Date()
    })

    // 尝试提取需求
    if (messages.value.length <= 4) {
      await tryExtractRequirements()
    }

    nextTick(() => {
      scrollToBottom()
    })
  } catch (error: any) {
    console.error('发送消息失败:', error)
    ElMessage.error(error.response?.data?.detail || '发送失败')
  } finally {
    loading.value = false
  }
}

// 发送示例问题
const sendExample = (text: string) => {
  inputMessage.value = text
  handleSend()
}

// 尝试提取需求
const tryExtractRequirements = async () => {
  try {
    const allMessages = messages.value.map(m => m.content).join('\n')
    const data = await extractRequirements(allMessages)
    requirements.value = data as TravelRequirements
  } catch (error) {
    // 静默失败，不影响聊天
    console.log('需求提取失败:', error)
  }
}

// 从对话中提取需求
const extractFromChat = async () => {
  if (messages.value.length === 0) {
    ElMessage.warning('请先与AI对话')
    return
  }

  extracting.value = true
  try {
    const allMessages = messages.value.map(m => m.content).join('\n')
    const data = await extractRequirements(allMessages)
    requirements.value = data as TravelRequirements
    ElMessage.success('需求提取成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '提取失败')
  } finally {
    extracting.value = false
  }
}

// 生成攻略
const generateGuide = async () => {
  if (!requirements.value) {
    ElMessage.warning('请先提取旅行需求')
    return
  }

  generatingGuide.value = true
  try {
    const response: any = await generateGuide({
      destination: requirements.value.destination,
      days: requirements.value.days,
      attractions: []
    })

    guideContent.value = formatMarkdown(response.guide)
    guideDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    generatingGuide.value = false
  }
}

// 复制攻略
const copyGuide = () => {
  const text = guideContent.value.replace(/<[^>]*>/g, '')
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

// 前往规划页面
const goToPlan = () => {
  if (!requirements.value?.destination) {
    ElMessage.warning('请先提取目的地信息')
    return
  }
  router.push({
    path: '/map',
    query: {
      city: requirements.value.destination
    }
  })
}

// 清空对话
const clearChat = () => {
  messages.value = []
  requirements.value = null
  inputMessage.value = ''
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 格式化消息
const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

// 格式化Markdown
const formatMarkdown = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

// 格式化时间
const formatTime = (date: Date) => {
  return dayjs(date).format('HH:mm:ss')
}
</script>

<style scoped>
.chat-view {
  height: calc(100vh - 100px);
}

.chat-container {
  height: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.messages-container {
  height: calc(100vh - 320px);
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.welcome-message h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.welcome-message p {
  margin: 0 0 20px 0;
  color: #606266;
}

.example-questions p {
  margin-bottom: 10px;
  font-size: 14px;
  color: #909399;
}

.example-questions .el-tag {
  margin: 5px;
  cursor: pointer;
}

.message {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.user-message .message-avatar {
  background: #67c23a;
  margin-left: 10px;
}

.assistant-message .message-avatar {
  margin-right: 10px;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
}

.user-message .message-text {
  background: #409eff;
  color: white;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  padding: 0 5px;
}

.typing-indicator {
  padding: 12px 16px;
}

.typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

.input-container {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.input-container .el-input {
  flex: 1;
}

.info-panel {
  height: 100%;
  overflow-y: auto;
}

.requirements-info {
  padding: 10px 0;
}

.guide-content {
  line-height: 1.8;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 60vh;
  overflow-y: auto;
}
</style>

