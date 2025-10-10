<template>
  <div class="ultimate-planner">
    <!-- 左侧：AI对话 + 偏好设置 (25%) -->
    <div class="left-sidebar" style="width: 25%">
      <div class="sidebar-header">
        <h3>🤖 AI旅行助手</h3>
        <el-button-group size="small">
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
      </div>

      <!-- 偏好设置（可折叠） -->
      <el-collapse v-model="activeCollapse" class="preferences-collapse">
        <el-collapse-item name="preferences">
          <template #title>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span>⚙️ 行程参数</span>
              <el-badge 
                v-if="selectedDestinations.length > 0" 
                :value="selectedDestinations.length" 
                type="primary"
              />
            </div>
          </template>
          <!-- 出发地 -->
          <div class="pref-section">
            <div class="pref-title">🏠 出发地</div>
            <el-cascader
              v-model="departureCity"
              :options="chinaRegions"
              :props="cascaderProps"
              placeholder="选择出发城市"
              clearable
              filterable
              size="small"
              style="width: 100%"
              @change="handleDepartureCityChange"
              @visible-change="() => {}"
            />
          </div>

          <!-- 目的地 -->
          <div class="pref-section">
            <div class="pref-title">📍 目的地（可多选）</div>
            <div class="destinations-list">
              <el-tag
                v-for="dest in selectedDestinations"
                :key="dest"
                closable
                @close="removeDestination(dest)"
                type="primary"
                size="small"
              >
                {{ dest }}
              </el-tag>
            </div>
            <el-cascader
              v-model="tempDestination"
              :options="chinaRegions"
              :props="cascaderProps"
              placeholder="选择省/市/区"
              clearable
              filterable
              size="small"
              style="width: 100%"
              @change="(val: any) => handleDestinationChange(val)"
              @visible-change="() => {}"
            />
          </div>

          <!-- 出发时间 -->
          <div class="pref-section">
            <div class="pref-title">🕐 出发时间</div>
            <el-date-picker
              v-model="preferences.departureDate"
              type="date"
              placeholder="选择日期"
              size="small"
              style="width: 100%"
              :disabled-date="disabledDate"
              format="YYYY-MM-DD"
            />
          </div>

          <!-- 天数 -->
          <div class="pref-section">
            <div class="pref-title">📅 旅行天数</div>
            <el-radio-group v-model="preferences.days" size="small">
              <el-radio-button :label="1">1天</el-radio-button>
              <el-radio-button :label="2">2天</el-radio-button>
              <el-radio-button :label="3">3天</el-radio-button>
              <el-radio-button :label="4">4天</el-radio-button>
              <el-radio-button :label="5">5天</el-radio-button>
              <el-radio-button :label="7">7天</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 出发交通方式 -->
          <div class="pref-section">
            <div class="pref-title">🚗 出发交通方式</div>
            <el-radio-group v-model="preferences.departureMode" size="small">
              <el-radio-button label="driving">自驾</el-radio-button>
              <el-radio-button label="transit">公共交通</el-radio-button>
              <el-radio-button label="flying">飞机</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 预算 -->
          <div class="pref-section">
            <div class="pref-title">💰 总预算</div>
            <el-select v-model="preferences.budget" size="small" style="width: 100%">
              <el-option label="¥500（穷游）" :value="500" />
              <el-option label="¥1000（经济）" :value="1000" />
              <el-option label="¥2000（舒适）" :value="2000" />
              <el-option label="¥3000（标准）" :value="3000" />
              <el-option label="¥5000（宽裕）" :value="5000" />
              <el-option label="¥10000（豪华）" :value="10000" />
              <el-option label="自定义" :value="0" />
            </el-select>
            <el-input-number
              v-if="preferences.budget === 0"
              v-model="customBudget"
              :min="100"
              :step="100"
              size="small"
              style="width: 100%; margin-top: 8px"
              placeholder="输入预算金额"
            />
          </div>

          <el-divider style="margin: 12px 0" />

          <!-- 同行伙伴 -->
          <div class="pref-section">
            <div class="pref-title">👥 同行伙伴</div>
            <el-radio-group v-model="preferences.companion" size="small">
              <el-radio-button label="独自" />
              <el-radio-button label="家庭" />
              <el-radio-button label="情侣" />
              <el-radio-button label="朋友" />
            </el-radio-group>
          </div>

          <!-- 风格偏好 -->
          <div class="pref-section">
            <div class="pref-title">🎨 风格偏好</div>
            <el-checkbox-group v-model="preferences.styles" size="small">
              <el-checkbox label="文化" />
              <el-checkbox label="自然" />
              <el-checkbox label="历史" />
              <el-checkbox label="美食" />
            </el-checkbox-group>
          </div>

          <!-- 行程节奏 -->
          <div class="pref-section">
            <div class="pref-title">⚡ 行程节奏</div>
            <el-radio-group v-model="preferences.pace" size="small">
              <el-radio-button label="紧凑" />
              <el-radio-button label="宽松" />
            </el-radio-group>
          </div>

          <!-- 住宿偏好 -->
          <div class="pref-section">
            <div class="pref-title">🏨 住宿偏好</div>
            <el-select v-model="preferences.accommodation" size="small" style="width: 100%">
              <el-option label="经济型（¥100-200/晚）" value="经济型" />
              <el-option label="舒适型（¥200-400/晚）" value="舒适型" />
              <el-option label="高档型（¥400-800/晚）" value="高档型" />
              <el-option label="豪华型（¥800+/晚）" value="豪华型" />
            </el-select>
          </div>

          <!-- 其他偏好 -->
          <div class="pref-section">
            <div class="pref-title">📝 其他说明</div>
            <el-input
              v-model="preferences.other"
              type="textarea"
              :rows="2"
              maxlength="100"
              show-word-limit
              placeholder="如：不喜欢爬山、喜欢摄影..."
              size="small"
            />
          </div>

          <!-- 生成按钮 -->
          <el-button
            type="primary"
            @click="generateWithSettings"
            :loading="generating"
            size="small"
            style="width: 100%; margin-top: 12px"
          >
            <el-icon><MagicStick /></el-icon>
            根据设置生成行程
          </el-button>
        </el-collapse-item>
      </el-collapse>

      <!-- AI对话区 -->
      <div class="chat-area">
        <div class="chat-messages" ref="messagesContainer">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-content" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>

        <div class="chat-input">
          <div class="quick-settings" @click="activeCollapse = activeCollapse.length === 0 ? ['preferences'] : []" style="cursor: pointer;">
            <el-text size="small" type="info">
              {{ formatDepartureTime() ? `🕐 ${formatDepartureTime()}` : '' }}
              {{ selectedDestinations.length > 0 ? ` 📍 ${selectedDestinations.join('、')}` : '⚠️ 请选择目的地' }}
              • {{ preferences.days }}天
              • ¥{{ preferences.budget === 0 ? customBudget : preferences.budget }}
              • {{ preferences.departureMode === 'driving' ? '🚗自驾' : preferences.departureMode === 'flying' ? '✈️飞机' : '🚄公交' }}
              <el-icon style="margin-left: 8px;"><Setting /></el-icon>
            </el-text>
          </div>
          <el-input
            v-model="userInput"
            type="textarea"
            :rows="2"
            placeholder="输入额外需求，或直接点击上方'根据设置生成行程'"
            @keydown.ctrl.enter="sendMessage"
            size="small"
          />
          <el-button
            type="primary"
            @click="sendMessage"
            :loading="generating"
            :disabled="selectedDestinations.length === 0"
            size="small"
            style="margin-top: 8px; width: 100%"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>

    <!-- 中间：可拖拽行程编辑 (35%) -->
    <div class="center-content" style="width: 35%">
      <div class="content-header">
        <div>
          <h2>{{ itinerary?.destination || '行程规划' }}{{ itinerary?.days ? `${itinerary.days}日游` : '' }}</h2>
          <div v-if="itinerary" class="quick-stats">
            <el-tag size="small" type="info">{{ totalAttractions }}个景点</el-tag>
            <el-tag size="small" type="warning">¥{{ itinerary.cost_breakdown?.total || 0 }}</el-tag>
          </div>
        </div>
        <el-space>
          <el-button @click="smartOptimize" :loading="optimizing" size="small">
            <el-icon><Connection /></el-icon>
            智能优化
          </el-button>
          <el-button type="primary" @click="saveTrip" size="small">
            <el-icon><DocumentChecked /></el-icon>
            保存
          </el-button>
        </el-space>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!itinerary" description="在左侧输入需求，AI会为您生成行程">
        <template #image>
          <div style="font-size: 64px">✈️</div>
        </template>
      </el-empty>

      <!-- 行程内容（可拖拽） -->
      <div v-else class="itinerary-editor">
        <!-- 待安排区域 -->
        <div class="pending-zone">
          <div class="zone-header">
            <span>📦 待安排区域 ({{ pendingItems.filter(item => !item.day || item.day === 0).length }})</span>
            <el-button text size="small" @click="showSearch = true">
              <el-icon><Search /></el-icon>
              搜索添加
            </el-button>
          </div>
          <div class="items-container">
            <draggable
              :model-value="pendingItems.filter(item => !item.day || item.day === 0)"
              @update:model-value="updatePendingItems"
              :group="{ name: 'schedule', pull: 'clone', put: true }"
              item-key="id"
              @end="onDragEnd"
            >
            <template #item="{ element }">
              <div>
                <div class="schedule-item pending">
                  <div class="item-header">
                    <strong>{{ element.name }}</strong>
                    <el-button
                      text
                      size="small"
                      @click="removeItem(element.id)"
                      :icon="Delete"
                    />
                  </div>
                  <div class="item-meta" v-if="element.cost">
                    <el-tag size="small">¥{{ element.cost }}</el-tag>
                  </div>
                </div>
              </div>
            </template>
            </draggable>
          </div>
        </div>

        <!-- 每日完整行程（所有地点可拖拽，交通自动生成） -->
        <div
          v-for="day in itinerary.daily_schedule"
          :key="day.day"
          class="day-schedule"
        >
          <!-- 天标题卡片 -->
          <div class="day-title-card">
            <div class="day-title-left">
              <h3>
                第{{ day.day }}天
                <span class="day-date">{{ getDayDateString(day.day) }}</span>
              </h3>
              <span class="day-theme" v-if="day.theme">{{ day.theme }}</span>
            </div>
            <div class="day-stats">
              <el-tag size="small" type="primary">{{ pendingItems.filter(item => item.day === day.day).length }}个地点</el-tag>
              <el-tag size="small" type="warning">¥{{ calculateDayCost(day) }}</el-tag>
            </div>
          </div>

          <!-- 完整时间线（昨日住宿 -> 景点 -> 今日住宿，全部可拖拽） -->
          <div class="full-timeline">
            <!-- 起点：出发地（第1天）或昨日住宿（第2天及以后） -->
            <div 
              v-if="day.day === 1 && departureCity.length > 0"
              class="location-card departure"
              @click="() => {}"
            >
              <div class="card-badge">出发地</div>
              <div class="card-icon">🏠</div>
              <div class="card-content">
                <h4>{{ departureCity[departureCity.length - 1] }}</h4>
                <p class="card-address">
                  {{ formatDepartureTime() }} · 
                  {{ preferences.departureMode === 'driving' ? '自驾出发' : preferences.departureMode === 'flying' ? '乘飞机' : '公共交通' }}
                </p>
              </div>
            </div>
            
            <div 
              v-else-if="day.day > 1 && getPreviousDayHotel(day.day - 1)"
              class="location-card prev-hotel"
              @click="selectItem(getPreviousDayHotel(day.day - 1))"
            >
              <div class="card-badge">昨晚</div>
              <div class="card-icon">🏨</div>
              <div class="card-content">
                <h4>{{ getPreviousDayHotel(day.day - 1).name }}</h4>
                <p class="card-address">{{ getPreviousDayHotel(day.day - 1).address }}</p>
              </div>
            </div>

            <!-- 地点列表（可拖拽） -->
            <draggable
              :model-value="getDayLocations(day.day)"
              @update:model-value="updateDayLocations(day.day, $event)"
              :group="{ name: 'locations', pull: true, put: true }"
              item-key="id"
              @end="() => onDayChange(day.day)"
              class="locations-draggable"
            >
              <template #item="{ element }">
                <div>
                  <!-- 自动生成的交通（从上一个地点到此地点） -->
                  <div 
                    v-if="element.autoTransport"
                    class="auto-transport"
                  >
                    <div class="transport-line" :class="{ 'transport-departure': element.autoTransport.isDeparture }">
                      <div class="transport-icon">{{ element.autoTransport.icon }}</div>
                      <div class="transport-text">
                        <div v-if="element.autoTransport.isDeparture" style="font-weight: 600;">
                          {{ element.autoTransport.from }} → {{ element.autoTransport.to }}
                        </div>
                        <div>
                          <span v-if="element.autoTransport.isLoading" style="color: #909399;">
                            正在获取路线信息...
                          </span>
                          <span v-else>
                            {{ element.autoTransport.type }}
                            <span v-if="element.autoTransport.departStation && element.autoTransport.arrivalStation">
                              · {{ element.autoTransport.departStation }} → {{ element.autoTransport.arrivalStation }}
                            </span>
                            <span v-if="element.autoTransport.departTime && element.autoTransport.arrivalTime">
                              · {{ element.autoTransport.departTime }} - {{ element.autoTransport.arrivalTime }}
                            </span>
                            <span v-if="element.autoTransport.route"> · {{ element.autoTransport.route }}</span>
                            <span v-if="element.autoTransport.distance"> · {{ element.autoTransport.distance }}</span>
                            <span v-if="!element.autoTransport.departTime">
                              · {{ element.autoTransport.duration }}
                            </span>
                            · ¥{{ element.autoTransport.cost }}
                            <span v-if="element.autoTransport.seatType" style="color: #67c23a; font-size: 11px;">
                              · {{ element.autoTransport.seatType }}
                            </span>
                            <span v-if="element.autoTransport.note" style="color: #909399; font-size: 11px;"> {{ element.autoTransport.note }}</span>
                            <el-tooltip 
                              v-if="element.autoTransport.aiTips" 
                              :content="element.autoTransport.aiTips"
                              placement="top"
                            >
                              <el-icon style="margin-left: 4px; color: #409eff; cursor: help;">
                                <InfoFilled />
                              </el-icon>
                            </el-tooltip>
                            <a 
                              v-if="element.autoTransport.queryUrl && !element.autoTransport.trainNum" 
                              :href="element.autoTransport.queryUrl" 
                              target="_blank"
                              style="margin-left: 8px; color: #409eff; text-decoration: none; font-size: 11px;"
                              @click.stop
                            >
                              🔍查询车次
                            </a>
                            <el-button
                              v-if="element.autoTransport.isDeparture && (element.autoTransport.type.includes('高铁') || element.autoTransport.type.includes('动车'))"
                              size="small"
                              :type="element.autoTransport.trainNum ? 'success' : 'primary'"
                              text
                              style="margin-left: 8px; padding: 0 4px; height: 20px; font-size: 11px;"
                              @click.stop="openTrainDialog(element)"
                            >
                              {{ element.autoTransport.trainNum ? `✏️${element.autoTransport.trainNum}` : '✏️填写车次' }}
                            </el-button>
                            <el-button
                              v-if="element.autoTransport.isDeparture && element.autoTransport.type.includes('飞机')"
                              size="small"
                              :type="element.autoTransport.flightNum ? 'success' : 'primary'"
                              text
                              style="margin-left: 8px; padding: 0 4px; height: 20px; font-size: 11px;"
                              @click.stop="openFlightDialog(element)"
                            >
                              {{ element.autoTransport.flightNum ? `✏️${element.autoTransport.flightNum}` : '✏️填写航班' }}
                            </el-button>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 地点卡片（景点或住宿） -->
                  <div 
                    class="location-card"
                    :class="[element.locationType, { selected: selectedItem?.id === element.id }]"
                    @click="selectItem(element)"
                  >
                    <div class="card-badge">{{ element.time || (element.locationType === 'hotel' ? '住宿' : '') }}</div>
                    <div class="card-icon">
                      {{ element.locationType === 'hotel' ? '🏨' : '📍' }}
                    </div>
                    <div class="card-image">
                      <img :src="element.image || (element.locationType === 'hotel' ? generateHotelImage(element.name) : generateAttractionImage(element.name))" :alt="element.name" @error="handleImageError" />
                    </div>
                    <div class="card-content">
                      <h4>{{ element.name }}</h4>
                      <div class="card-tags">
                        <el-tag size="small" v-if="element.duration_hours">
                          {{ element.duration_hours }}小时
                        </el-tag>
                        <el-tag size="small" type="warning">
                          ¥{{ element.locationType === 'hotel' ? element.price_per_night + '/晚' : element.cost }}
                        </el-tag>
                        <el-tag size="small" type="info" v-if="element.type">
                          {{ element.type }}
                        </el-tag>
                      </div>
                      <p class="card-tips" v-if="element.tips">💡 {{ element.tips }}</p>
                      <p class="card-address" v-if="element.address">📮 {{ element.address }}</p>
                    </div>
                    <div class="card-actions">
                      <el-button
                        text
                        size="small"
                        type="danger"
                        @click.stop="removeLocation(element.id, day.day)"
                        :icon="Delete"
                      />
                    </div>
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：地图 + 详情 (40%) -->
    <div class="right-sidebar" style="width: 40%">
      <div class="map-header">
        <h4>🗺️ 智能地图</h4>
        <el-space wrap>
          <!-- 出发地信息 -->
          <el-tag v-if="departureCity.length > 0" size="small" type="success">
            🏠 {{ departureCity[departureCity.length - 1] }}
          </el-tag>
          
          <!-- 地图图层控制 -->
          <el-dropdown size="small">
            <el-button size="small">
              图层 <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="toggleLayer('route')">
                  <el-checkbox v-model="mapLayers.route" />
                  显示路线
                </el-dropdown-item>
                <el-dropdown-item @click="toggleLayer('traffic')">
                  <el-checkbox v-model="mapLayers.traffic" />
                  实时路况
                </el-dropdown-item>
                <el-dropdown-item @click="toggleLayer('poi')">
                  <el-checkbox v-model="mapLayers.poi" />
                  周边POI
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 天数选择 -->
          <el-select
            v-model="selectedDay"
            size="small"
            placeholder="选择天"
            style="width: 100px"
            @change="updateMapView"
          >
            <el-option label="全览" :value="0" />
            <el-option
              v-for="d in itinerary?.daily_schedule || []"
              :key="d.day"
              :label="`第${d.day}天`"
              :value="d.day"
            />
          </el-select>
          
          <!-- 地图类型 -->
          <el-radio-group v-model="mapType" size="small" @change="changeMapType">
            <el-radio-button label="normal">标准</el-radio-button>
            <el-radio-button label="satellite">卫星</el-radio-button>
          </el-radio-group>
        </el-space>
      </div>

      <!-- 地图容器 -->
      <div ref="mapContainer" class="map-container">
        <!-- 地图统计信息浮层 - 紧凑版 -->
        <div v-if="mapStats.visible && itinerary" class="map-stats-overlay">
          <div class="stats-grid">
            <div class="stats-item">
              <span class="label">📍</span>
              <span class="value">{{ mapStats.attractionCount }}个</span>
            </div>
            <div class="stats-item">
              <span class="label">💰</span>
              <span class="value">¥{{ (itinerary.cost_breakdown?.total || 0).toFixed(0) }}</span>
            </div>
          </div>
        </div>
        
        <!-- 地图控制按钮 -->
        <div class="map-controls">
          <el-button-group size="small">
            <el-button @click="zoomIn" :icon="Plus" />
            <el-button @click="zoomOut" :icon="Minus" />
            <el-button @click="resetView" :icon="Aim">定位</el-button>
          </el-button-group>
        </div>
        
        <!-- 路线图例 -->
        <div v-if="mapLayers.route && itinerary" class="route-legend">
          <div style="font-weight: 600; margin-bottom: 8px;">路线图例</div>
          <div class="route-legend-item">
            <div class="route-legend-line walking" :style="{color: getDayColor(1)}"></div>
            <span>步行</span>
          </div>
          <div class="route-legend-item">
            <div class="route-legend-line driving" :style="{color: getDayColor(1)}"></div>
            <span>驾车/出租</span>
          </div>
          <div class="route-legend-item">
            <div class="route-legend-line transit" :style="{color: getDayColor(1)}"></div>
            <span>公交/地铁</span>
          </div>
          <div class="route-legend-item" style="margin-top: 8px;">
            <div style="width: 20px; height: 20px; background: #52c41a; border-radius: 50%; border: 2px solid white;"></div>
            <span>出发地</span>
          </div>
          <div class="route-legend-item">
            <div style="width: 20px; height: 20px; background: #409eff; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;">1</div>
            <span>景点</span>
          </div>
          <div class="route-legend-item">
            <div style="width: 20px; height: 20px; background: #e6a23c; border-radius: 50%; border: 2px solid white;"></div>
            <span>酒店</span>
          </div>
        </div>
      </div>

      <!-- 详情面板 -->
      <transition name="slide-up">
        <div v-if="selectedItem" class="detail-panel">
          <div class="detail-header">
            <h4>{{ selectedItem.name }}</h4>
            <el-button text @click="selectedItem = null" :icon="Close" size="small" />
          </div>
          <div class="detail-body">
            <div class="detail-row" v-if="selectedItem.type">
              <span class="label">类型</span>
              <el-tag size="small">{{ selectedItem.type }}</el-tag>
            </div>
            <div class="detail-row" v-if="selectedItem.rating">
              <span class="label">评分</span>
              <el-rate
                :model-value="selectedItem.rating"
                disabled
                show-score
                size="small"
              />
            </div>
            <div class="detail-row" v-if="selectedItem.address">
              <span class="label">地址</span>
              <span class="value">{{ selectedItem.address }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.cost !== undefined && selectedItem.cost > 0">
              <span class="label">费用</span>
              <span class="value">¥{{ selectedItem.cost }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.tel">
              <span class="label">电话</span>
              <span class="value">{{ selectedItem.tel }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.opentime">
              <span class="label">营业时间</span>
              <span class="value">{{ selectedItem.opentime }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.business_area">
              <span class="label">商圈</span>
              <el-tag size="small" type="success">{{ selectedItem.business_area }}</el-tag>
            </div>
            <div class="detail-row" v-if="selectedItem.tips">
              <span class="label">建议</span>
              <div class="tips">{{ selectedItem.tips }}</div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 搜索对话框（增强版） -->
    <el-dialog 
      v-model="showSearch" 
      title="🔍 搜索景点/地点" 
      width="700px"
      :close-on-click-modal="false"
    >
      <div class="search-dialog-content">
        <!-- 搜索输入 -->
        <div class="search-input-section">
          <el-select
            v-model="searchCity"
            placeholder="选择城市"
            filterable
            style="width: 150px; margin-right: 10px;"
          >
            <el-option 
              v-for="dest in selectedDestinations" 
              :key="dest" 
              :label="dest" 
              :value="dest" 
            />
            <el-option 
              v-if="selectedDestinations.length === 0 && itinerary?.destination" 
              :label="itinerary.destination" 
              :value="itinerary.destination" 
            />
          </el-select>
          <el-autocomplete
            v-model="searchKeyword"
            :fetch-suggestions="fetchSuggestions"
            placeholder="输入景点、酒店、餐厅等名称"
            clearable
            @select="handleSuggestionSelect"
            @keyup.enter="performSearch"
            :trigger-on-focus="false"
            :debounce="300"
            style="flex: 1;"
            popper-class="search-autocomplete-popper"
          >
            <template #prepend>
              <el-icon><Search /></el-icon>
            </template>
            <template #append>
              <el-button @click="performSearch" :loading="searching" type="primary">
                搜索
              </el-button>
            </template>
            <template #default="{ item }">
              <div class="suggestion-item">
                <div class="suggestion-icon">
                  <el-icon :color="getTypeColor(item.type)">
                    <component :is="getTypeIcon(item.type)" />
                  </el-icon>
                </div>
                <div class="suggestion-content">
                  <div class="suggestion-name">{{ item.name }}</div>
                  <div class="suggestion-meta">
                    <el-tag size="small" :type="getTagType(item.type)" effect="plain">
                      {{ getTypeName(item.type) }}
                    </el-tag>
                    <span class="suggestion-address">{{ item.address }}</span>
                  </div>
                </div>
              </div>
            </template>
          </el-autocomplete>
        </div>

        <!-- 分类筛选 -->
        <div class="search-categories">
          <el-radio-group v-model="searchCategory" size="small" @change="performSearch">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="110000">景点</el-radio-button>
            <el-radio-button label="100000">酒店</el-radio-button>
            <el-radio-button label="050000">餐饮</el-radio-button>
            <el-radio-button label="060000">购物</el-radio-button>
            <el-radio-button label="070000">生活服务</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 搜索结果 -->
        <div class="search-results" v-loading="searching">
          <el-empty 
            v-if="searchResults.length === 0 && !searching" 
            description="输入关键词搜索地点"
            :image-size="80"
          />
          <div
            v-for="result in searchResults"
            :key="result.id"
            class="result-item"
            @click="addSearchResult(result)"
          >
            <div class="result-icon">
              <el-icon :size="24" :color="getTypeColor(result.type)">
                <component :is="getTypeIcon(result.type)" />
              </el-icon>
            </div>
            <div class="result-content">
              <div class="result-header">
                <strong class="result-name">{{ result.name }}</strong>
                <el-tag 
                  v-if="result.type" 
                  size="small" 
                  type="info"
                  effect="plain"
                >
                  {{ getTypeName(result.type) }}
                </el-tag>
              </div>
              <div class="result-address">
                <el-icon><Location /></el-icon>
                {{ result.address || '暂无地址' }}
              </div>
              <div class="result-meta">
                <span v-if="result.rating && result.rating > 0">
                  <el-icon><Star /></el-icon>
                  {{ result.rating }}分
                </span>
                <span v-if="result.cost">
                  <el-icon><Money /></el-icon>
                  ¥{{ result.cost }}
                </span>
                <span v-if="result.business_area">
                  <el-icon><Location /></el-icon>
                  {{ result.business_area }}
                </span>
                <span v-if="result.tel">
                  <el-icon><Phone /></el-icon>
                  {{ result.tel }}
                </span>
              </div>
              <div class="result-extra" v-if="result.opentime">
                <el-text size="small" type="info">
                  🕐 {{ result.opentime }}
                </el-text>
              </div>
            </div>
            <div class="result-action">
              <el-button size="small" type="primary" plain>
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
          </div>
        </div>

        <!-- 搜索提示 -->
        <div class="search-tips" v-if="!searching && searchResults.length === 0">
          <el-alert
            title="搜索提示"
            type="info"
            :closable="false"
            show-icon
          >
            <ul>
              <li>输入景点名称，如"天安门"、"故宫"</li>
              <li>输入地标建筑，如"东方明珠"、"广州塔"</li>
              <li>输入酒店、餐厅等名称进行搜索</li>
              <li>选择不同分类可缩小搜索范围</li>
            </ul>
          </el-alert>
        </div>
      </div>
    </el-dialog>
    
    <!-- 航班信息填写对话框（增强版：省市筛选） -->
    <el-dialog 
      v-model="showFlightDialog" 
      title="✈️ 填写航班信息" 
      width="650px"
      @close="resetFlightForm"
    >
      <el-form :model="flightForm" label-width="100px" size="small">
        <el-form-item label="航班号">
          <el-input 
            v-model="flightForm.flightNum" 
            placeholder="如：CA1234、MU5678" 
            clearable
          >
            <template #prepend>✈️</template>
          </el-input>
        </el-form-item>
        
        <el-divider content-position="left">出发机场</el-divider>
        
        <el-form-item label="出发省市">
          <el-select
            v-model="flightForm.departProvince"
            placeholder="选择省/市"
            filterable
            clearable
            style="width: 100%"
            @change="updateDepartAirports"
          >
            <el-option
              v-for="province in airportProvinces"
              :key="province"
              :label="province"
              :value="province"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="出发机场">
          <el-select
            v-model="flightForm.departAirport"
            placeholder="选择机场"
            filterable
            clearable
            style="width: 100%"
            :disabled="!flightForm.departProvince"
          >
            <el-option
              v-for="airport in filteredDepartAirports"
              :key="airport.iata"
              :label="`${airport.name} (${airport.iata}) - ${airport.city}`"
              :value="airport.name"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ airport.name }}</span>
                <el-tag size="small" type="primary">{{ airport.iata }}</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">到达机场</el-divider>
        
        <el-form-item label="到达省市">
          <el-select
            v-model="flightForm.arrivalProvince"
            placeholder="选择省/市"
            filterable
            clearable
            style="width: 100%"
            @change="updateArrivalAirports"
          >
            <el-option
              v-for="province in airportProvinces"
              :key="province"
              :label="province"
              :value="province"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="到达机场">
          <el-select
            v-model="flightForm.arrivalAirport"
            placeholder="选择机场"
            filterable
            clearable
            style="width: 100%"
            :disabled="!flightForm.arrivalProvince"
          >
            <el-option
              v-for="airport in filteredArrivalAirports"
              :key="airport.iata"
              :label="`${airport.name} (${airport.iata}) - ${airport.city}`"
              :value="airport.name"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ airport.name }}</span>
                <el-tag size="small" type="success">{{ airport.iata }}</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">航班时间</el-divider>
        
        <el-form-item label="起飞时间">
          <el-time-picker
            v-model="flightForm.departTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="降落时间">
          <el-time-picker
            v-model="flightForm.arrivalTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="舱位类型">
          <el-select v-model="flightForm.cabinClass" style="width: 100%">
            <el-option label="头等舱" value="头等舱" />
            <el-option label="商务舱" value="商务舱" />
            <el-option label="超级经济舱" value="超级经济舱" />
            <el-option label="经济舱" value="经济舱" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="票价(元)">
          <el-input-number 
            v-model="flightForm.price" 
            :min="0" 
            :step="50"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showFlightDialog = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveFlightInfo" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 火车票信息填写对话框 -->
    <el-dialog 
      v-model="showTrainDialog" 
      title="填写火车票信息" 
      width="500px"
      @close="resetTrainForm"
    >
      <el-form :model="trainForm" label-width="80px" size="small">
        <el-form-item label="车次号">
          <el-input 
            v-model="trainForm.trainNum" 
            placeholder="如：G123" 
            clearable
          >
            <template #prepend>🚄</template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="出发站">
          <el-autocomplete
            v-model="trainForm.departStation"
            :fetch-suggestions="searchStations"
            placeholder="输入车站名称搜索"
            style="width: 100%"
            clearable
          >
            <template #prepend>🏁</template>
          </el-autocomplete>
        </el-form-item>
        
        <el-form-item label="到达站">
          <el-autocomplete
            v-model="trainForm.arrivalStation"
            :fetch-suggestions="searchStations"
            placeholder="输入车站名称搜索"
            style="width: 100%"
            clearable
          >
            <template #prepend>🏁</template>
          </el-autocomplete>
        </el-form-item>
        
        <el-form-item label="出发时间">
          <el-time-picker
            v-model="trainForm.departTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="到达时间">
          <el-time-picker
            v-model="trainForm.arrivalTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="座位类型">
          <el-select v-model="trainForm.seatType" style="width: 100%">
            <el-option label="商务座" value="商务座" />
            <el-option label="特等座" value="特等座" />
            <el-option label="一等座" value="一等座" />
            <el-option label="二等座" value="二等座" />
            <el-option label="硬卧" value="硬卧" />
            <el-option label="软卧" value="软卧" />
            <el-option label="硬座" value="硬座" />
            <el-option label="无座" value="无座" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="票价(元)">
          <el-input-number 
            v-model="trainForm.price" 
            :min="0" 
            :step="10"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showTrainDialog = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveTrainInfo" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElNotification, ElTimePicker } from 'element-plus'
import {
  RefreshLeft, RefreshRight, Delete, Search, Connection,
  DocumentChecked, Close, MagicStick, ArrowDown, Plus, Minus, Aim, Setting,
  Calendar, InfoFilled, Location, Star, Money, Phone, Place, House, Food, 
  ShoppingCart, Service
} from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import AMapLoader from '@amap/amap-jsapi-loader'
import { chinaRegions } from '@/components/chinaRegions'
import { searchAttractions, getInputTips } from '@/api/attraction'
import { airports, searchAirportsByName } from '@/components/airportCodes'

// 状态
const userInput = ref('')
const messages = ref<any[]>([])
const generating = ref(false)
const itinerary = ref<any>(null)
const selectedDay = ref(0)
const selectedItem = ref<any>(null)
const weatherData = ref<any>(null)  // 天气数据
const showSearch = ref(false)
const searching = ref(false)
const searchKeyword = ref('')
const searchResults = ref<any[]>([])
const searchCity = ref('')
const searchCategory = ref('')
const optimizing = ref(false)

// 火车票填写对话框
const showTrainDialog = ref(false)
const currentTransport = ref<any>(null)  // 当前要填写的交通信息
const trainForm = reactive({
  trainNum: '',        // 车次号
  departStation: '',   // 出发站
  arrivalStation: '',  // 到达站
  departTime: '',      // 出发时间
  arrivalTime: '',     // 到达时间
  seatType: '二等座',  // 座位类型
  price: 0,            // 票价
  duration: ''         // 时长
})
const stationSuggestions = ref<string[]>([])  // 车站建议列表
const loadingStations = ref(false)

// 航班填写对话框
const showFlightDialog = ref(false)
const flightForm = reactive({
  flightNum: '',          // 航班号
  departProvince: '',     // 出发省市
  departAirport: '',      // 出发机场
  arrivalProvince: '',    // 到达省市
  arrivalAirport: '',     // 到达机场
  departTime: '',         // 起飞时间
  arrivalTime: '',        // 降落时间
  cabinClass: '经济舱',    // 舱位类型
  price: 0,               // 票价
  duration: ''            // 飞行时长
})

// 机场数据
const airportProvinces = computed(() => {
  const provinces = new Set<string>()
  airports.forEach(airport => {
    provinces.add(airport.region)
  })
  return Array.from(provinces).sort((a, b) => a.localeCompare(b, 'zh-CN'))
})

const filteredDepartAirports = computed(() => {
  if (!flightForm.departProvince) return []
  return airports.filter(airport => airport.region === flightForm.departProvince)
})

const filteredArrivalAirports = computed(() => {
  if (!flightForm.arrivalProvince) return []
  return airports.filter(airport => airport.region === flightForm.arrivalProvince)
})

// 偏好
const activeCollapse = ref<string[]>(['preferences'])
const preferences = reactive({
  departureDate: new Date(),
  departureMode: 'transit',  // driving: 自驾, transit: 公共交通, flying: 飞机
  days: 3,
  budget: 3000,
  companion: '独自',
  styles: ['文化'],
  pace: '宽松',
  accommodation: '舒适型',
  other: ''
})

// 禁用过去的日期
function disabledDate(date: Date) {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

// 出发地和目的地
const departureCity = ref<any[]>([])
const selectedDestinations = ref<string[]>([])
const tempDestination = ref<any[]>([])
const customBudget = ref(0)

// 级联配置
const cascaderProps = {
  expandTrigger: 'hover' as const,
  checkStrictly: true,
  emitPath: true,
  label: 'label',
  value: 'value',
  children: 'children',
  // 兼容性配置
  multiple: false,
  lazy: false
}

// 待安排区域
const pendingItems = ref<any[]>([])

// 撤销/重做
const history = ref<any[]>([])
const historyIndex = ref(-1)

// 地图
const mapContainer = ref<HTMLElement | null>(null)
const map = ref<any>(null)
const messagesContainer = ref<HTMLElement | null>(null)
const mapType = ref('normal')
const mapLayers = reactive({
  route: true,
  traffic: false,
  poi: true
})
const mapStats = reactive({
  visible: false,
  attractionCount: 0
})
const markers = ref<any[]>([])
const polylines = ref<any[]>([])

// 计算属性
const totalAttractions = computed(() => {
  if (!itinerary.value?.daily_schedule) return 0
  return itinerary.value.daily_schedule.reduce((sum: number, day: any) => 
    sum + (day.attractions?.length || 0), 0
  )
})

onMounted(() => {
  initMap()
  
  // 欢迎消息
  messages.value.push({
    role: 'assistant',
    content: '您好！我是AI旅行助手 🤖<br>告诉我您的需求，我会生成包含<b>景点、住宿、交通、费用</b>的完整行程。'
  })
  
  // 键盘快捷键
  window.addEventListener('keydown', handleKeyboard)
})

// 检测IPv6环境并给出友好提示
async function checkIPv6Environment() {
  try {
    const response = await fetch('/api/v1/location/debug')
    const data = await response.json()
    
    const detectedIP = data.detected_ip
    const isPrivate = data.is_private
    const isIPv6 = detectedIP && detectedIP.includes(':') && detectedIP.split(':').length >= 2
    
    if (isIPv6 || !detectedIP || isPrivate) {
      ElNotification({
        title: '💡 自动定位提示',
        dangerouslyUseHTMLString: true,
        message: `
          <div style="line-height: 1.6;">
            <p><strong>检测到您的网络环境可能无法自动定位：</strong></p>
            ${isIPv6 ? '<p>• 您使用的是IPv6网络（高德API仅支持IPv4）</p>' : ''}
            ${isPrivate || !detectedIP ? '<p>• 您处于内网环境（如局域网）</p>' : ''}
            <p style="margin-top: 8px;"><strong>解决方案：</strong></p>
            <p>1️⃣ 在左侧"出发地"中手动选择城市</p>
            <p>2️⃣ 生产环境部署后，IPv4用户可自动定位</p>
            <p style="color: #909399; font-size: 12px; margin-top: 8px;">
              提示：这不影响您使用AI规划功能，只需手动选择城市即可
            </p>
          </div>
        `,
        type: 'info',
        duration: 8000,
        position: 'top-right'
      })
    }
  } catch (error) {
    console.log('[IPv6检测] 跳过检测')
  }
}

// 初始化地图
async function initMap() {
  try {
    console.log('[AI规划] 初始化地图...')
    
    // 加载高德地图
    ;(window as any)._AMapSecurityConfig = {
      securityJsCode: '647d226e39983ddf9a56349328a7e844'
    }

    const AMap = await AMapLoader.load({
      key: '542addb61a32fc4137e362202e48bce9',
      version: '2.0',
      plugins: [
        'AMap.Marker', 
        'AMap.Polyline', 
        'AMap.InfoWindow', 
        'AMap.Driving',
        'AMap.Walking',
        'AMap.Transfer',
        'AMap.TruckDriving',
        'AMap.Riding',
        'AMap.TrafficLayer',
        'AMap.Scale',
        'AMap.ToolBar',
        'AMap.TileLayer',
        'AMap.TileLayer.Satellite',
        'AMap.TileLayer.RoadNet',
        'AMap.Geolocation'  // 添加高德定位插件
      ]
    })
    
    // 保存AMap到window供其他函数使用
    ;(window as any).AMapInstance = AMap

    if (mapContainer.value) {
      map.value = new AMap.Map(mapContainer.value, {
        zoom: 11,
        center: [116.397428, 39.90923],  // 默认北京
        mapStyle: 'amap://styles/normal',
        viewMode: '2D',
        resizeEnable: true,
        showIndoorMap: false,
        dragEnable: true,  // 确保地图可拖动
        zoomEnable: true,   // 确保地图可缩放
        doubleClickZoom: true,  // 双击缩放
        scrollWheel: true   // 鼠标滚轮缩放
      })
      
      // 添加缩放控件
      map.value.addControl(new AMap.Scale())
      map.value.addControl(new AMap.ToolBar({
        position: 'RB'
      }))
      
      // 使用高德官方Geolocation插件（最快最准确）
      const geolocation = new AMap.Geolocation({
        enableHighAccuracy: false,
        timeout: 10000,
        useNative: true,  // 优先使用浏览器定位
        convert: true,  // 自动转换为高德坐标
        showButton: false,
        showMarker: false,
        showCircle: false,
        panToLocation: true,  // 定位成功后自动移动
        zoomToAccuracy: false
      })
      
      map.value.addControl(geolocation)
      
      // 检测IPv6环境并提示
      checkIPv6Environment()
    }
  } catch (error) {
    console.error('地图加载失败:', error)
  }
}

// 地图图层控制
function toggleLayer(layer: string) {
  mapLayers[layer] = !mapLayers[layer]
  
  if (layer === 'traffic' && map.value) {
    if (mapLayers.traffic) {
      const trafficLayer = new (window as any).AMap.TileLayer.Traffic({
        zIndex: 10
      })
      map.value.add(trafficLayer)
    } else {
      map.value.getAllOverlays('TileLayer').forEach((layer: any) => {
        if (layer.className === 'AMap.TileLayer.Traffic') {
          map.value.remove(layer)
        }
      })
    }
  }
  
  updateMapView()
}

// 切换地图类型
function changeMapType(type: string) {
  if (!map.value) return
  
  const AMap = (window as any).AMap
  
  if (type === 'satellite') {
    // 卫星图需要使用图层方式
    map.value.setLayers([
      new AMap.TileLayer.Satellite(),
      new AMap.TileLayer.RoadNet()  // 添加路网
    ])
  } else {
    // 标准地图
    map.value.setLayers([
      new AMap.TileLayer()
    ])
  }
}

// 地图控制
function zoomIn() {
  if (map.value) {
    map.value.zoomIn()
  }
}

function zoomOut() {
  if (map.value) {
    map.value.zoomOut()
  }
}

function resetView() {
  if (map.value && itinerary.value) {
    updateMapView(true)  // 重置视图时自动适应
  }
}

// 更新地图视图（防止重复调用）
let updateMapDebounceTimer: any = null
let _isFirstMapUpdate = true  // 标记首次更新

async function updateMapView(autoFit: boolean = false) {
  // 防抖：避免频繁调用
  if (updateMapDebounceTimer) {
    clearTimeout(updateMapDebounceTimer)
  }
  
  updateMapDebounceTimer = setTimeout(async () => {
    await _updateMapViewInternal(autoFit || _isFirstMapUpdate)
    _isFirstMapUpdate = false  // 首次更新后设为false
  }, 500)
}

// 内部地图更新函数
async function _updateMapViewInternal(autoFit: boolean = false) {
  if (!map.value || !itinerary.value) return
  
  console.log('更新地图视图...')
  
  // 清除现有标记和线
  clearMapOverlays()
  
  const AMap = (window as any).AMap
  const points: any[] = []
  
  // 添加出发地标记（如果有）
  if (departureCity.value.length > 0 && itinerary.value.daily_schedule.length > 0) {
    const departureName = departureCity.value[departureCity.value.length - 1]
    const firstDay = itinerary.value.daily_schedule[0]
    const firstAttr = firstDay.attractions[0]
    
    if (firstAttr && firstAttr.lng && firstAttr.lat && departureName !== itinerary.value.destination) {
      // 添加出发地标记（特殊样式）
      try {
        // 调用高德API获取出发地坐标
        const response = await fetch(`/api/v1/attractions/search?city=${departureName}&keyword=${departureName}&limit=1`)
        const data = await response.json()
        
        if (data && data.length > 0) {
          const departurePoint = data[0]
          
          const departureMarker = new AMap.Marker({
            position: [departurePoint.lng, departurePoint.lat],
            title: `出发地：${departureName}`,
            icon: new AMap.Icon({
              size: new AMap.Size(32, 32),
              image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-marker.png',
              imageSize: new AMap.Size(32, 32)
            }),
            label: {
              content: `<div style="background: #52c41a; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">🏠 出发地</div>`,
              direction: 'top',
              offset: new AMap.Pixel(0, -10)
            }
          })
          
          map.value.add(departureMarker)
          markers.value.push(departureMarker)
          points.push([departurePoint.lng, departurePoint.lat])
          
          // 绘制出发地到第一个景点的路线（增强版）
          if (mapLayers.route) {
            const distance = calculateDistance(
              departurePoint.lng, 
              departurePoint.lat, 
              firstAttr.lng, 
              firstAttr.lat
            )
            const transportMode = distance > 100 ? 'transit' : distance > 50 ? 'driving' : 'transit'
            
            await drawRoute(
              [departurePoint.lng, departurePoint.lat],
              [firstAttr.lng, firstAttr.lat],
              transportMode,
              '#52c41a',
              AMap,
              departureCity.value || '出发地',
              firstAttr.name
            )
          }
        }
      } catch (error) {
        console.error('获取出发地坐标失败:', error)
      }
    }
  }
  
  // 添加景点标记
  const daysToShow = selectedDay.value === 0 
    ? itinerary.value.daily_schedule 
    : itinerary.value.daily_schedule.filter((d: any) => d.day === selectedDay.value)
  
  let attractionIndex = 0
  for (const day of daysToShow) {
    for (const attr of day.attractions) {
      if (attr.lng && attr.lat) {
        attractionIndex++
        
        // 创建景点标记（带数字）
        const marker = new AMap.Marker({
          position: [attr.lng, attr.lat],
          title: attr.name,
          icon: new AMap.Icon({
            size: new AMap.Size(32, 32),
            image: 'data:image/svg+xml;base64,' + btoa(`
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">
                <circle cx="16" cy="16" r="14" fill="${getDayColor(day.day)}" stroke="white" stroke-width="2"/>
                <text x="16" y="21" text-anchor="middle" fill="white" font-size="14" font-weight="bold">${attractionIndex}</text>
              </svg>
            `),
            imageSize: new AMap.Size(32, 32)
          }),
          label: {
            content: `<div style="background: ${getDayColor(day.day)}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; white-space: nowrap;">${attr.name}</div>`,
            direction: 'top',
            offset: new AMap.Pixel(0, -5)
          },
          extData: { ...attr, day: day.day, type: 'attraction' }
        })
        
        // 点击标记显示信息窗口
        marker.on('click', () => {
          const infoWindow = new AMap.InfoWindow({
            content: `
              <div class="info-window">
                <h4>${attr.name}</h4>
                <p>📅 第${day.day}天 ${attr.start_time || ''}</p>
                <p>⏱️ 游玩${attr.duration_hours || 1}小时</p>
                <p>💰 ¥${attr.cost || 0}</p>
                ${attr.tips ? `<p>💡 ${attr.tips}</p>` : ''}
              </div>
            `,
            offset: new AMap.Pixel(0, -30)
          })
          infoWindow.open(map.value, marker.getPosition())
          selectItem(attr)
        })
        
        map.value.add(marker)
        markers.value.push(marker)
        points.push([attr.lng, attr.lat])
      }
    }
    
    // 绘制实际道路路线（按交通方式）
    if (mapLayers.route && day.attractions.length > 0) {
      await drawDayRoute(day, AMap)
    }
    
    // 添加酒店标记
    if (day.hotel && day.hotel.address) {
      // 如果酒店已有坐标，直接使用
      if (day.hotel.lng && day.hotel.lat) {
        const hotelInfo = day.hotel
        addHotelMarker(hotelInfo, day)
      } else {
        // 尝试获取酒店坐标（使用缓存避免重复请求）
        const cacheKey = `hotel_${day.hotel.name}`
        if (!window._hotelCache) window._hotelCache = {}
        
        if (window._hotelCache[cacheKey]) {
          addHotelMarker(window._hotelCache[cacheKey], day)
        } else {
          try {
            const city = itinerary.value.destination || selectedDestinations.value[0] || '北京'
            const hotelData = await searchAttractions({
              city: city,
              keyword: day.hotel.name,
              limit: 1
            })
            
            if (hotelData && hotelData.length > 0) {
              window._hotelCache[cacheKey] = hotelData[0]
              addHotelMarker(hotelData[0], day)
            }
          } catch (error) {
            console.error('获取酒店位置失败:', error)
          }
        }
      }
    }
  }
  
  // 自适应视野（仅在autoFit=true时执行，避免频繁调整）
  if (autoFit && points.length > 0) {
    setTimeout(() => {
      if (map.value) {
        map.value.setFitView(null, false, [80, 80, 80, 80])  // 添加边距
      }
    }, 800)  // 等待所有路线绘制完成
  }
  
  // 更新统计信息
  updateMapStats()
}

// 添加酒店标记的辅助函数
function addHotelMarker(hotelInfo: any, day: any) {
  const AMap = (window as any).AMap
  if (!map.value || !hotelInfo || !hotelInfo.lng || !hotelInfo.lat || !day.hotel) return
  
  // 创建简单的酒店图标（避免btoa中文编码问题）
  const hotelMarker = new AMap.Marker({
    position: [hotelInfo.lng, hotelInfo.lat],
    title: day.hotel.name,
    icon: new AMap.Icon({
      size: new AMap.Size(36, 36),
      image: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36">
          <circle cx="18" cy="18" r="16" fill="#e6a23c" stroke="white" stroke-width="2"/>
          <text x="18" y="24" text-anchor="middle" fill="white" font-size="18">H</text>
        </svg>
      `),
      imageSize: new AMap.Size(36, 36)
    }),
    label: {
      content: `<div style="background: #e6a23c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">住宿</div>`,
      direction: 'bottom',
      offset: new AMap.Pixel(0, 5)
    },
    extData: { ...day.hotel, type: 'hotel', day: day.day }
  })
  
  hotelMarker.on('click', () => {
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div class="info-window">
          <h4>🏨 ${day.hotel.name}</h4>
          <p>📅 第${day.day}天住宿</p>
          <p>💰 ¥${day.hotel.price_per_night}/晚</p>
          ${day.hotel.address ? `<p>📮 ${day.hotel.address}</p>` : ''}
          ${day.hotel.reason ? `<p>💡 ${day.hotel.reason}</p>` : ''}
        </div>
      `,
      offset: new AMap.Pixel(0, -30)
    })
    infoWindow.open(map.value, hotelMarker.getPosition())
    selectItem(day.hotel)
  })
  
  map.value.add(hotelMarker)
  markers.value.push(hotelMarker)
  
  // 从最后一个景点到酒店的路线（增强版）
  if (mapLayers.route && day.attractions && day.attractions.length > 0) {
    const lastAttr = day.attractions[day.attractions.length - 1]
    if (lastAttr.lng && lastAttr.lat && hotelInfo.lng && hotelInfo.lat) {
      const distance = calculateDistance(lastAttr.lng, lastAttr.lat, hotelInfo.lng, hotelInfo.lat)
      const transportMode = distance < 2 ? 'walking' : distance < 10 ? 'transit' : 'driving'
      
      drawRoute(
        [lastAttr.lng, lastAttr.lat],
        [hotelInfo.lng, hotelInfo.lat],
        transportMode,
        getDayColor(day.day),
        AMap,
        lastAttr.name,
        hotelInfo.name
      )
    }
  }
}

// 清除地图覆盖物
function clearMapOverlays() {
  markers.value.forEach(marker => map.value.remove(marker))
  polylines.value.forEach(line => map.value.remove(line))
  markers.value = []
  polylines.value = []
}

// 获取每天的颜色
function getDayColor(day: number) {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[(day - 1) % colors.length]
}

// 绘制某一天的完整路线
async function drawDayRoute(day: any, AMap: any) {
  const attractions = day.attractions.filter((a: any) => a.lng && a.lat)
  
  console.log(`绘制第${day.day}天路线，共${attractions.length}个景点`)
  
  for (let i = 0; i < attractions.length - 1; i++) {
    const from = attractions[i]
    const to = attractions[i + 1]
    
    // 计算距离决定交通方式（优化：防止过长路段使用步行）
    const distance = calculateDistance(from.lng, from.lat, to.lng, to.lat)
    const transportMode = distance < 1.5 ? 'walking' : distance < 10 ? 'transit' : 'driving'
    
    console.log(`  ${from.name} → ${to.name}: ${distance.toFixed(2)}km, 使用${transportMode}`)
    
    try {
      await drawRoute(
        [from.lng, from.lat],
        [to.lng, to.lat],
        transportMode,
        getDayColor(day.day),
        AMap,
        from.name,  // 起点名称
        to.name     // 终点名称
      )
    } catch (error) {
      console.error(`绘制路线失败 ${from.name} → ${to.name}:`, error)
    }
    
    // 添加延迟避免API限制
    await new Promise(resolve => setTimeout(resolve, 200))
  }
  
  console.log(`第${day.day}天路线绘制完成`)
}

// 绘制两点之间的实际路线（增强版）
function drawRoute(
  start: [number, number],
  end: [number, number],
  mode: 'walking' | 'driving' | 'transit',
  color: string,
  AMap: any,
  fromName?: string,
  toName?: string
) {
  return new Promise((resolve) => {
    try {
      if (mode === 'walking') {
        // 步行路线
        const walking = new AMap.Walking({
          map: map.value
        })
        
        walking.search(start, end, (status: string, result: any) => {
          if (status === 'complete' && result.routes && result.routes.length > 0) {
            const route = result.routes[0]
            
            // 高德API返回的path可能在route.steps中
            let pathData = route.path
            if (!pathData || !Array.isArray(pathData) || pathData.length === 0) {
              // 尝试从steps中提取path
              if (route.steps && Array.isArray(route.steps)) {
                pathData = []
                route.steps.forEach((step: any) => {
                  if (step.path && Array.isArray(step.path)) {
                    pathData = pathData.concat(step.path)
                  }
                })
              }
            }
            
            // 如果还是没有有效路径，使用起止点直线
            if (!pathData || !Array.isArray(pathData) || pathData.length === 0) {
              console.warn('步行路线无详细路径，使用直线', route)
              drawStraightLine(start, end, color, 'solid')
              resolve(true)
              return
            }
            
            // 绘制路径（带箭头方向）
            const polyline = new AMap.Polyline({
              path: pathData,
              strokeColor: color,
              strokeWeight: 5,
              strokeOpacity: 0.8,
              strokeStyle: 'solid',
              showDir: true,  // 显示方向箭头
              dirColor: '#fff',
              lineJoin: 'round',
              lineCap: 'round'
            })
            // 标记路线所属天数（用于后续删除）
            polyline._dayColor = color
            map.value.add(polyline)
            polylines.value.push(polyline)
            
            // 添加路线信息标记（中点位置）
            const midIndex = Math.floor(pathData.length / 2)
            const midPoint = pathData[midIndex]
            addRouteInfoMarker(
              midPoint,
              {
                mode: '🚶 步行',
                distance: `${(route.distance / 1000).toFixed(2)}km`,
                duration: `${Math.ceil(route.time / 60)}分钟`,
                cost: '免费',
                from: fromName,
                to: toName
              },
              color,
              AMap
            )
            
            console.log('步行路线绘制完成')
          } else {
            console.warn('步行路线搜索失败，使用直线')
            drawStraightLine(start, end, color, 'solid')
          }
          resolve(true)
        })
        
      } else if (mode === 'driving') {
        // 驾车路线
        const driving = new AMap.Driving({
          policy: 0,  // 0: 最快捷模式
          ferry: 1,
          map: map.value
        })
        
        driving.search(start, end, (status: string, result: any) => {
          if (status === 'complete' && result.routes && result.routes.length > 0) {
            const route = result.routes[0]
            
            // 高德API返回的path可能在route.steps中
            let pathData = route.path
            if (!pathData || !Array.isArray(pathData) || pathData.length === 0) {
              // 尝试从steps中提取path
              if (route.steps && Array.isArray(route.steps)) {
                pathData = []
                route.steps.forEach((step: any) => {
                  if (step.path && Array.isArray(step.path)) {
                    pathData = pathData.concat(step.path)
                  }
                })
              }
            }
            
            // 如果还是没有有效路径，使用起止点直线
            if (!pathData || !Array.isArray(pathData) || pathData.length === 0) {
              console.warn('驾车路线无详细路径，使用直线', route)
              drawStraightLine(start, end, color, 'solid')
              resolve(true)
              return
            }
            
            // 绘制路径（更粗的线条）
            const polyline = new AMap.Polyline({
              path: pathData,
              strokeColor: color,
              strokeWeight: 6,
              strokeOpacity: 0.9,
              strokeStyle: 'solid',
              showDir: true,
              dirColor: '#fff',
              lineJoin: 'round',
              lineCap: 'round'
            })
            polyline._dayColor = color
            map.value.add(polyline)
            polylines.value.push(polyline)
            
            // 计算出租车费用（起步价13元 + 2.3元/km）
            const distance = route.distance / 1000
            const taxiCost = 13 + distance * 2.3
            
            // 添加路线信息标记
            const midIndex = Math.floor(pathData.length / 2)
            const midPoint = pathData[midIndex]
            addRouteInfoMarker(
              midPoint,
              {
                mode: '🚗 驾车/出租',
                distance: `${distance.toFixed(2)}km`,
                duration: `${Math.ceil(route.time / 60)}分钟`,
                cost: `约¥${taxiCost.toFixed(0)}`,
                from: fromName,
                to: toName
              },
              color,
              AMap
            )
            
            console.log('驾车路线绘制完成')
          } else {
            console.warn('驾车路线搜索失败，使用直线')
            drawStraightLine(start, end, color, 'solid')
          }
          resolve(true)
        })
        
      } else {
        // 公交路线 - 使用Transfer API
        console.log('绘制公交路线')
        const transfer = new AMap.Transfer({
          map: map.value,
          policy: AMap.TransferPolicy.LEAST_TIME,  // 时间最短
          city: '当前城市'  // 需要传入城市名
        })
        
        transfer.search(start, end, (status: string, result: any) => {
          if (status === 'complete' && result.plans && result.plans.length > 0) {
            const plan = result.plans[0]
            
            // 验证segments数据
            if (!plan.segments || !Array.isArray(plan.segments) || plan.segments.length === 0) {
              console.warn('公交路线segments数据无效，使用直线')
              drawStraightLine(start, end, color, 'dashed')
              resolve(true)
              return
            }
            
            // 绘制公交路线的各个segment
            plan.segments.forEach((segment: any) => {
              // 验证segment的路径数据
              if (!segment) return
              
              let pathData = segment.path
              // 如果没有path，尝试使用起止点
              if (!pathData || !Array.isArray(pathData) || pathData.length === 0) {
                if (segment.start_location && segment.end_location) {
                  pathData = [segment.start_location, segment.end_location]
                } else {
                  return  // 跳过无效的segment
                }
              }
              
              if (segment.transit_mode === 'WALK') {
                // 步行段 - 虚线
                const polyline = new AMap.Polyline({
                  path: pathData,
                  strokeColor: color,
                  strokeWeight: 3,
                  strokeOpacity: 0.7,
                  strokeStyle: 'dashed'
                })
                polyline._dayColor = color
                map.value.add(polyline)
                polylines.value.push(polyline)
              } else {
                // 公交/地铁段 - 实线
                const polyline = new AMap.Polyline({
                  path: pathData,
                  strokeColor: color,
                  strokeWeight: 5,
                  strokeOpacity: 0.9,
                  strokeStyle: 'solid',
                  showDir: true
                })
                polyline._dayColor = color
                map.value.add(polyline)
                polylines.value.push(polyline)
              }
            })
            
            // 添加路线信息标记
            const midPoint = [
              (start[0] + end[0]) / 2,
              (start[1] + end[1]) / 2
            ]
            addRouteInfoMarker(
              midPoint,
              {
                mode: '🚇 公交/地铁',
                distance: `${(plan.distance / 1000).toFixed(2)}km`,
                duration: `${Math.ceil(plan.time / 60)}分钟`,
                cost: `约¥${plan.cost || 3}`,
                transfers: `换乘${plan.segments.length - 1}次`,
                from: fromName,
                to: toName
              },
              color,
              AMap
            )
            
            console.log('公交路线绘制完成')
          } else {
            console.warn('公交路线搜索失败，使用直线')
            drawStraightLine(start, end, color, 'dashed')
          }
          resolve(true)
        })
      }
    } catch (error) {
      console.error('绘制路线失败:', error)
      drawStraightLine(start, end, color, 'dashed')
      resolve(false)
    }
  })
}

// 添加路线信息标记（悬浮显示交通详情）
function addRouteInfoMarker(
  position: [number, number],
  info: {
    mode: string
    distance: string
    duration: string
    cost: string
    transfers?: string
    from?: string
    to?: string
  },
  color: string,
  AMap: any
) {
  // 创建自定义HTML内容
  const content = `
    <div style="
      background: ${color};
      color: white;
      padding: 8px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      white-space: nowrap;
      cursor: pointer;
      backdrop-filter: blur(10px);
    ">
      <div style="display: flex; align-items: center; gap: 6px;">
        <span>${info.mode}</span>
        <span style="opacity: 0.9;">•</span>
        <span>${info.distance}</span>
        <span style="opacity: 0.9;">•</span>
        <span>${info.duration}</span>
        <span style="opacity: 0.9;">•</span>
        <span>${info.cost}</span>
      </div>
    </div>
  `
  
  const marker = new AMap.Marker({
    position: position,
    content: content,
    offset: new AMap.Pixel(-50, -15),
    zIndex: 100
  })
  
  // 标记为路线信息标记（用于后续删除）
  marker._dayColor = color
  marker._isRouteInfo = true
  
  // 点击标记显示详细信息
  const infoWindow = new AMap.InfoWindow({
    content: `
      <div style="padding: 10px; min-width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: #303133;">${info.mode}</h4>
        <div style="color: #606266; font-size: 13px; line-height: 1.8;">
          ${info.from ? `<div><strong>起点：</strong>${info.from}</div>` : ''}
          ${info.to ? `<div><strong>终点：</strong>${info.to}</div>` : ''}
          <div><strong>距离：</strong>${info.distance}</div>
          <div><strong>时间：</strong>${info.duration}</div>
          <div><strong>费用：</strong>${info.cost}</div>
          ${info.transfers ? `<div><strong>换乘：</strong>${info.transfers}</div>` : ''}
        </div>
      </div>
    `,
    offset: new AMap.Pixel(0, -30)
  })
  
  marker.on('click', () => {
    infoWindow.open(map.value, position)
  })
  
  map.value.add(marker)
  markers.value.push(marker)
}

// 绘制直线（备用方案）
function drawStraightLine(
  start: [number, number],
  end: [number, number],
  color: string,
  style: 'solid' | 'dashed' = 'dashed'
) {
  const AMap = (window as any).AMap
  const polyline = new AMap.Polyline({
    path: [start, end],
    strokeColor: color,
    strokeWeight: 4,
    strokeOpacity: 0.7,
    strokeStyle: style,
    showDir: true
  })
  polyline._dayColor = color
  map.value.add(polyline)
  polylines.value.push(polyline)
}

// 更新地图统计（简化版：只统计景点数量，费用从cost_breakdown获取）
function updateMapStats() {
  if (!itinerary.value) {
    mapStats.visible = false
    return
  }
  
  let count = 0
  itinerary.value.daily_schedule.forEach((day: any) => {
    count += day.attractions?.length || 0
  })
  
  mapStats.visible = true
  mapStats.attractionCount = count
}

// 处理出发地变化
function handleDepartureCityChange(value: any) {
  // 防止多次触发和验证警告
  if (!value || !Array.isArray(value)) return
  console.log('出发地已选择:', value[value.length - 1])
}

// 处理目的地变化
function handleDestinationChange(value: string[] | string | null | undefined) {
  // 防止多次触发
  if (!value) return
  
  try {
    // 确保value是数组
    const valueArray = Array.isArray(value) ? value : [value]
    
    if (valueArray.length > 0) {
      const destName = valueArray[valueArray.length - 1]
      if (destName && !selectedDestinations.value.includes(destName)) {
        selectedDestinations.value.push(destName)
        
        // 异步清空选择器
        nextTick(() => {
          tempDestination.value = []
        })
      }
    }
  } catch (error) {
    console.error('处理目的地变化错误:', error)
  }
}

// 移除目的地
function removeDestination(dest: string) {
  const index = selectedDestinations.value.indexOf(dest)
  if (index > -1) {
    selectedDestinations.value.splice(index, 1)
  }
}

// 根据设置生成行程
async function generateWithSettings() {
  if (selectedDestinations.value.length === 0) {
    ElMessage.warning('请先选择目的地')
    return
  }

  const destination = selectedDestinations.value[0]
  const departure = departureCity.value.length > 0 ? departureCity.value[departureCity.value.length - 1] : ''
  const budget = preferences.budget === 0 ? customBudget.value : preferences.budget

  let message = `我想`
  if (departure) {
    message += `从${departure}出发，`
  }
  
  // 添加出发日期信息
  if (preferences.departureDate) {
    const departDate = new Date(preferences.departureDate)
    const dateStr = `${departDate.getMonth() + 1}月${departDate.getDate()}日`
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const weekday = weekdays[departDate.getDay()]
    message += `计划${dateStr}（星期${weekday}）出发，`
  }
  
  message += `去${selectedDestinations.value.join('、')}旅行，玩${preferences.days}天，预算${budget}元。`

  userInput.value = message
  
  // 自动折叠偏好设置面板
  activeCollapse.value = []
  
  await sendMessage()
}

// 发送消息
async function sendMessage() {
  if (!userInput.value.trim() && selectedDestinations.value.length === 0) return

  let message = userInput.value.trim()

  // 如果没有手动输入，根据设置构建
  if (!message && selectedDestinations.value.length > 0) {
    const destination = selectedDestinations.value[0]
    const departure = departureCity.value.length > 0 ? departureCity.value[departureCity.value.length - 1] : ''
    const budget = preferences.budget === 0 ? customBudget.value : preferences.budget
    
    message = `我想`
    if (departure) {
      message += `从${departure}出发，`
    }
    message += `去${destination}玩${preferences.days}天，预算${budget}元`
  }

  // 添加偏好
  const prefInfo = buildPreferencesInfo()
  if (prefInfo) {
    message = `${message}\n偏好：${prefInfo}`
  }

  messages.value.push({
    role: 'user',
    content: userInput.value.trim() || `去${selectedDestinations.value.join('、')}`
  })

  userInput.value = ''
  scrollToBottom()

  generating.value = true
  thinkingCollapsed = false  // 重置折叠状态
  chunk_received = 0  // 重置chunk计数器

  const progressIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '<div class="ai-thinking">🤔 正在分析...</div>'
  })

  try {
    console.log('发送请求到流式API...')
    
    // 格式化出发日期
    let departureDateStr = ''
    if (preferences.departureDate) {
      const date = new Date(preferences.departureDate)
      departureDateStr = date.toISOString().split('T')[0]  // YYYY-MM-DD格式
    }
    
    const response = await fetch('/api/v1/agent/enhanced-stream', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      body: JSON.stringify({
        message,
        destination: selectedDestinations.value.join('、') || extractDestination(message),
        days: extractDays(message),
        budget: extractBudget(message),
        preferences: preferences.styles,
        departureDate: departureDateStr  // 添加出发日期
      })
    })

    console.log('响应状态:', response.status, response.headers.get('content-type'))

    if (!response.ok) {
      const errorText = await response.text()
      console.error('API错误:', errorText)
      throw new Error('生成失败: ' + errorText)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    if (reader) {
      console.log('开始读取流式数据...')
      let chunkCount = 0
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          console.log(`流式数据读取完成，共收到 ${chunkCount} 个数据块`)
          break
        }

        chunkCount++
        const decoded = decoder.decode(value, { stream: true })
        buffer += decoded
        
        // 按行分割（SSE标准是\n分隔）
        const lines = buffer.split('\n')
        // 保留最后一个不完整的行
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim()) continue  // 跳过空行
          if (line.startsWith(':')) continue  // 跳过注释（心跳包）
          
          // 处理 "data: " 开头的行
          if (line.startsWith('data:')) {
            try {
              // 移除 "data: " 前缀（可能有多个）
              let jsonStr = line
              while (jsonStr.startsWith('data:')) {
                jsonStr = jsonStr.substring(5).trim()
              }
              
              if (jsonStr) {
                const event = JSON.parse(jsonStr)
                console.log(`[SSE #${chunkCount}] ${event.type}:`, event.content?.substring(0, 50))
                handleStreamEvent(event, progressIndex)
              }
            } catch (e) {
              // JSON解析失败，可能是分段的，忽略
            }
          }
        }
      }
    }

    // 清理stream标记并关闭main-content
    if (messages.value[progressIndex]) {
      let content = messages.value[progressIndex].content
      content = content.replace(/<!-- STREAM -->/g, '')
      content = content.replace(/<!-- LLM_STREAM -->/g, '')
      // 如果有main-content，关闭它
      if (content.includes('<div class="main-content">')) {
        content += '</div>'
      }
      messages.value[progressIndex].content = content
    }

    if (itinerary.value) {
      messages.value.push({
        role: 'assistant',
        content: `<div class="success-msg">✅ 行程已生成！共${totalAttractions.value}个景点，总费用¥${itinerary.value.cost_breakdown?.total || 0}<br>您可以拖拽调整景点顺序，或点击地图查看详情 →</div>`
      })
      
      // 生成完成后展开偏好设置（方便下次修改）
      nextTick(() => {
        setTimeout(() => {
          // 可以选择性展开，或保持折叠
          // activeCollapse.value = ['preferences']
        }, 1000)
      })
    }

  } catch (error: any) {
    console.error('生成失败:', error)
    messages.value.splice(progressIndex, 1)
    messages.value.push({
      role: 'assistant',
      content: `<div class="error-msg">❌ 生成失败：${error.message}</div>`
    })
  } finally {
    generating.value = false
    scrollToBottom()
  }
}

// 处理流式事件
let thinkingCollapsed = false  // 标记思考内容是否已折叠
let chunk_received = 0  // 累计接收的chunk数量

function handleStreamEvent(event: any, progressIndex: number) {
  console.log('[事件处理] 类型:', event.type, '内容:', event.content?.substring(0, 50))
  
  if (!messages.value[progressIndex]) {
    console.warn('[事件处理] 消息索引无效:', progressIndex)
    return
  }
  
  switch (event.type) {
    case 'start':
      // Agent开始
      console.log('[事件处理] Agent启动')
      messages.value[progressIndex].content += `<div class="agent-start">🤖 ${event.content}</div>`
      scrollToBottom()
      break
    
    case 'thinking':
      // AI思考过程
      console.log('[事件处理] 添加thinking:', event.content)
      messages.value[progressIndex].content += `<div class="thinking-item">💭 ${event.content}</div>`
      scrollToBottom()
      break
      
    case 'tool_start':
      // 工具调用开始（显示详细的输入参数）
      console.log('[事件处理] 工具调用开始:', event.tool, event.input)
      let toolStartHtml = `<div class="tool-call">
        <div class="tool-call-header">🔧 调用工具：<strong>${event.tool}</strong></div>`
      
      // 如果有输入参数，显示JSON
      if (event.input && Object.keys(event.input).length > 0) {
        toolStartHtml += `<pre class="tool-input">${JSON.stringify(event.input, null, 2)}</pre>`
      }
      
      toolStartHtml += `</div>`
      messages.value[progressIndex].content += toolStartHtml
      scrollToBottom()
      break
      
    case 'tool_end':
      // 工具调用完成（显示详细的输出结果）
      console.log('[事件处理] 工具调用完成:', event.tool, event.output)
      let toolEndHtml = `<div class="tool-result">
        <div class="tool-result-header">✅ ${event.tool} 完成</div>`
      
      // 如果有输出结果，显示（限制长度）
      if (event.output) {
        const outputText = typeof event.output === 'string' ? event.output : JSON.stringify(event.output, null, 2)
        const displayOutput = outputText.length > 500 ? outputText.substring(0, 500) + '...' : outputText
        toolEndHtml += `<pre class="tool-output">${displayOutput}</pre>`
      }
      
      toolEndHtml += `</div>`
      messages.value[progressIndex].content += toolEndHtml
      scrollToBottom()
      break
      
    case 'llm_stream':
      // Agent的LLM流式回复
      console.log('[事件处理] LLM流式输出')
      let llmContent = messages.value[progressIndex].content
      const llmStreamMarker = '<!-- LLM_STREAM -->'
      
      // 第一次收到时，折叠思考和工具调用内容
      if (!thinkingCollapsed && !llmContent.includes(llmStreamMarker)) {
        console.log('[事件处理] 折叠工具调用记录')
        llmContent = `<details class="thinking-collapsed">
          <summary>💭 查看AI思考和工具调用过程（点击展开）</summary>
          ${llmContent}
        </details>
        <div class="main-content">`
        thinkingCollapsed = true
      }
      
      if (llmContent.includes(llmStreamMarker)) {
        llmContent = llmContent.replace(llmStreamMarker, event.content + llmStreamMarker)
      } else {
        llmContent += `<div class="ai-reply">${event.content}${llmStreamMarker}</div>`
      }
      
      messages.value[progressIndex].content = llmContent
      chunk_received++
      if (chunk_received % 5 === 0) {
        scrollToBottom()
      }
      break
      
    case 'deepseek':
      // DeepSeek深度推理过程（旧版兼容）
      console.log('[事件处理] 添加deepseek:', event.content)
      messages.value[progressIndex].content += `<div class="deepseek-item">🧠 ${event.content}</div>`
      scrollToBottom()
      break
      
    case 'deepseek_stream':
      // DeepSeek实时流式输出 - 第一次收到时折叠思考内容（旧版兼容）
      console.log('[事件处理] 添加deepseek_stream')
      let deepseekStreamContent = messages.value[progressIndex].content
      const deepseekMarker = '<!-- STREAM -->'
      
      // 第一次收到正文输出时，折叠思考内容
      if (!thinkingCollapsed && !deepseekStreamContent.includes(deepseekMarker)) {
        console.log('[事件处理] 折叠思考内容')
        // 将所有现有内容包装到折叠区域
        deepseekStreamContent = `<details class="thinking-collapsed">
          <summary>💭 查看AI思考过程（点击展开）</summary>
          ${deepseekStreamContent}
        </details>
        <div class="main-content">`
        thinkingCollapsed = true
      }
      
      if (deepseekStreamContent.includes(deepseekMarker)) {
        // 替换为最新内容（覆盖而不是追加）
        const regex = /<pre[^>]*>[\s\S]*?<!-- STREAM -->/
        deepseekStreamContent = deepseekStreamContent.replace(regex, `<pre style="white-space: pre-wrap; font-family: monospace; font-size: 11px; color: #666; line-height: 1.4; max-height: 400px; overflow-y: auto;">${event.content}${deepseekMarker}`)
      } else {
        // 创建新的流式内容区域
        deepseekStreamContent += `<div class="deepseek-stream">📝 正在生成行程...<pre style="white-space: pre-wrap; font-family: monospace; font-size: 11px; color: #666; line-height: 1.4; max-height: 400px; overflow-y: auto;">${event.content}${deepseekMarker}</pre></div>`
      }
      
      messages.value[progressIndex].content = deepseekStreamContent
      chunk_received++
      // 减少滚动频率
      if (chunk_received % 10 === 0) {
        scrollToBottom()
      }
      break
    
    case 'complete':
      // Agent完成（带最终回复）
      console.log('[事件处理] Agent完成')
      if (event.reply) {
        // 如果有完整回复，替换内容
        let completeContent = messages.value[progressIndex].content
        if (completeContent.includes('<div class="main-content">')) {
          completeContent += `<div class="final-reply">${event.reply}</div></div>`
        } else {
          completeContent += `<div class="final-reply">${event.reply}</div>`
        }
        messages.value[progressIndex].content = completeContent
      }
      scrollToBottom()
      break
    
    case 'done':
      // Agent完成信号
      console.log('[事件处理] Agent完成信号')
      scrollToBottom()
      break
      
    case 'error':
      // 错误处理
      console.error('[事件处理] Agent错误:', event.content)
      messages.value[progressIndex].content += `<div class="error-msg">❌ ${event.content}</div>`
      scrollToBottom()
      break
      
    case 'progress_detail':
      // 详细进度信息 - 动态更新
      if (messages.value[progressIndex]) {
        // 移除上一条进度信息（如果存在）
        const content = messages.value[progressIndex].content
        const lastProgressIndex = content.lastIndexOf('<div class="progress-detail">')
        if (lastProgressIndex > -1) {
          const beforeProgress = content.substring(0, lastProgressIndex)
          messages.value[progressIndex].content = beforeProgress
        }
        messages.value[progressIndex].content += `<div class="progress-detail">⏳ ${event.content}</div>`
        scrollToBottom()
      }
      break
      
    case 'status':
      // 状态更新 - 立即显示（重要信息）
      if (messages.value[progressIndex]) {
        messages.value[progressIndex].content += `<div class="status-item">${event.content}</div>`
        // 状态信息立即显示，不等待批量更新
        nextTick(() => scrollToBottom())
      }
      break
      
    case 'progress':
      // 进度更新 - 节流（每5个更新一次）
      if (messages.value[progressIndex] && event.current % 5 === 0) {
        const lastDiv = messages.value[progressIndex].content.split('<div class="status-item">').pop()
        messages.value[progressIndex].content = messages.value[progressIndex].content.replace(
          lastDiv || '',
          `🔍 正在获取景点信息... (${event.current}/${event.total}) ${event.name}</div>`
        )
        // 进度更新不频繁滚动
        if (event.current % 10 === 0) {
          scrollToBottom()
        }
      }
      break
      
    case 'tool_result':
      // 工具调用结果
      if (messages.value[progressIndex]) {
        let resultText = ''
        if (event.output.name) {
          resultText = `✓ ${event.tool}: ${event.output.name}`
        } else if (event.output.optimization_rate) {
          resultText = `✓ 第${event.output.day}天优化完成，节省${event.output.optimization_rate}路程`
        }
        messages.value[progressIndex].content += `<div class="tool-result">${resultText}</div>`
        scrollToBottom()
      }
      break
    
    case 'weather':
      // 接收天气数据
      console.log('收到天气数据:', event.data)
      weatherData.value = event.data
      
      // 显示天气消息
      const forecasts = event.data.forecasts || []
      if (forecasts.length > 0) {
        const weatherSummary = forecasts.slice(0, 3).map((f: any) => 
          `${f.date.slice(5)}: ${f.day_weather} ${f.day_temp}°C`
        ).join('、')
        addAIMessage(`🌤️ 天气预报：${weatherSummary}`)
      }
      break
      
    case 'itinerary':
      // 接收完整行程
      itinerary.value = event.data
      syncItineraryToItems()
      nextTick(() => updateMapView(true))  // 首次加载自动适应视野
      break
      
    case 'done':
      // 完成
      console.log('流式响应完成')
      break
  }
}

// 同步行程到可拖拽列表（包括景点和住宿）（防止循环调用）
let _syncingToItems = false
function syncItineraryToItems() {
  if (!itinerary.value || _syncingToItems) return

  _syncingToItems = true
  try {
    const newItems: any[] = []

    itinerary.value.daily_schedule?.forEach((day: any) => {
    // 添加景点
    day.attractions?.forEach((attr: any, index: number) => {
      // 优先使用真实照片，其次使用生成的默认图片
      const imageUrl = attr.thumbnail || 
                       (attr.photos && attr.photos.length > 0 ? attr.photos[0] : null) ||
                       attr.image || 
                       generateAttractionImage(attr.name)
      
      newItems.push({
        id: `attr-${day.day}-${index}`,
        day: day.day,
        locationType: 'attraction',
        time: attr.start_time,
        name: attr.name,
        cost: attr.cost,
        tips: attr.tips,
        start_time: attr.start_time,
        duration_hours: attr.duration_hours,
        address: attr.address,
        lng: attr.lng,
        lat: attr.lat,
        type: attr.type,
        image: imageUrl,
        photos: attr.photos || [],  // 保留所有照片
        thumbnail: attr.thumbnail || '',  // 保留缩略图
        ...attr
      })
    })
    
    // 添加住宿
    if (day.hotel) {
      newItems.push({
        id: `hotel-${day.day}`,
        day: day.day,
        locationType: 'hotel',
        time: '住宿',
        name: day.hotel.name,
        price_per_night: day.hotel.price_per_night,
        address: day.hotel.address,
        reason: day.hotel.reason,
        image: day.hotel.image || generateHotelImage(day.hotel.name),
        ...day.hotel
      })
    }
    
    // 保存AI建议的交通信息（用于后续智能决策）
    if (day.transportation && day.transportation.length > 0) {
      console.log(`第${day.day}天AI建议的交通:`, day.transportation)
      // 将AI的交通建议存储到day对象中，供generateAutoTransport参考
      day.ai_transport_suggestions = day.transportation
    }
  })

    pendingItems.value = newItems
    recordChange()
    
    console.log('同步完成:', newItems.length, '个地点（景点+住宿）')
  } finally {
    _syncingToItems = false
  }
}

// 生成景点默认图片（使用占位图）
function generateAttractionImage(name: string) {
  // 使用SVG占位图（避免emoji编码问题）
  const svg = `
    <svg width="80" height="60" xmlns="http://www.w3.org/2000/svg">
      <rect width="80" height="60" fill="#e3f2fd"/>
      <circle cx="40" cy="30" r="12" fill="#1976d2"/>
      <text x="40" y="36" text-anchor="middle" fill="white" font-size="14">POI</text>
    </svg>
  `
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
}

// 生成酒店默认图片
function generateHotelImage(name: string) {
  const svg = `
    <svg width="80" height="60" xmlns="http://www.w3.org/2000/svg">
      <rect width="80" height="60" fill="#fff3e0"/>
      <circle cx="40" cy="30" r="12" fill="#f57c00"/>
      <text x="40" y="36" text-anchor="middle" fill="white" font-size="16">H</text>
    </svg>
  `
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg)
}

// 获取某天的景点
function getDayAttractions(day: number) {
  return pendingItems.value.filter(item => item.day === day && item.locationType === 'attraction')
}

// 获取某天的所有地点（景点+住宿，异步生成交通）
function getDayLocations(day: number) {
  const locations = pendingItems.value.filter(item => item.day === day)
  
  // 按类型排序：景点在前，住宿在后
  const sorted = locations.sort((a, b) => {
    if (a.locationType === 'attraction' && b.locationType === 'hotel') return -1
    if (a.locationType === 'hotel' && b.locationType === 'attraction') return 1
    return 0
  })
  
  // 标记正在生成，避免重复调用
  sorted.forEach((loc, index, arr) => {
    // 检查是否需要生成交通信息（避免重复生成）
    if (loc._transportGenerating) {
      return  // 正在生成中，跳过
    }
    
    if (index > 0) {
      const prevLoc = arr[index - 1]
      // 异步获取交通信息（只在没有或加载失败时生成）
      if (!loc.autoTransport) {
        loc._transportGenerating = true
        generateAutoTransport(prevLoc, loc, day).then(transport => {
          loc.autoTransport = transport
          loc._transportGenerating = false
        }).catch(() => {
          loc._transportGenerating = false
        })
      }
    } else if (day === 1) {
      // 第一天第一个地点，从出发地出发
      if (departureCity.value.length > 0 && !loc.autoTransport) {
        const departureName = departureCity.value[departureCity.value.length - 1]
        loc._transportGenerating = true
        generateDepartureTransport(departureName, loc).then(transport => {
          loc.autoTransport = transport
          loc._transportGenerating = false
        }).catch(() => {
          loc._transportGenerating = false
        })
      }
    } else if (day > 1) {
      // 其他天第一个地点，从昨日住宿出发
      const prevHotel = getPreviousDayHotel(day - 1)
      if (prevHotel && !loc.autoTransport) {
        loc._transportGenerating = true
        generateAutoTransport(prevHotel, loc, day).then(transport => {
          loc.autoTransport = transport
          loc._transportGenerating = false
        }).catch(() => {
          loc._transportGenerating = false
        })
      }
    }
  })
  
  return sorted
}

// 生成从出发地的交通（增强版：支持机场/火车站中转）
async function generateDepartureTransport(departureName: string, firstLocation: any) {
  const mode = preferences.departureMode
  
  // 先获取出发地坐标
  try {
    const departureCoords = await searchCityCenter(departureName)
    const destCoords = [firstLocation.lng, firstLocation.lat]
    
    if (!departureCoords || !destCoords[0] || !destCoords[1]) {
      return getFallbackDepartureTransport(departureName, firstLocation, mode)
    }
    
    const AMap = (window as any).AMap
    const destinationCity = itinerary.value?.destination || selectedDestinations.value[0] || '目的地'
    
    // 计算直线距离
    const directDistance = calculateDistance(
      departureCoords[0], 
      departureCoords[1], 
      destCoords[0], 
      destCoords[1]
    )
    
    return new Promise((resolve) => {
      if (mode === 'driving') {
        // 自驾 - 直接到景点
        const driving = new AMap.Driving({
          policy: 0  // 0: 最快捷模式
        })
        
        driving.search(departureCoords, destCoords, (status: string, result: any) => {
          if (status === 'complete' && result.routes && result.routes.length > 0) {
            const route = result.routes[0]
            const distance = route.distance / 1000  // 转为公里
            const duration = Math.ceil(route.time / 60)  // 转为分钟
            const tollCost = Math.ceil(distance * 0.5)  // 过路费估算
            const fuelCost = Math.ceil(distance * 0.7)  // 油费估算（0.7元/公里）
            
            resolve({
              type: '自驾',
              icon: '🚗',
              duration: `${duration}分钟`,
              distance: `${distance.toFixed(1)}km`,
              cost: tollCost + fuelCost,
              from: `${departureName}（市中心）`,
              to: firstLocation.name,
              isDeparture: true,
              note: '直达目的地'
            })
          } else {
            resolve(getFallbackDepartureTransport(departureName, firstLocation, mode))
          }
        })
      } else if (mode === 'flying') {
        // 飞机 - 需要中转（出发地 → 机场 → 目的地机场 → 景点）
        // 这里简化为提示用户手动添加航班信息
        resolve({
          type: '飞机（需填写）',
          icon: '✈️',
          duration: `约${Math.ceil(directDistance / 600 * 60)}分钟`,
          distance: `${directDistance.toFixed(0)}km`,
          cost: Math.ceil(directDistance * 0.8),
          from: `${departureName}`,
          to: `${destinationCity}`,
          isDeparture: true,
          isManual: true,
          note: '请点击填写航班信息（出发地 → 机场 → 机场 → 景点）',
          segments: [
            { from: departureName, to: `${departureName}机场`, type: '地面交通' },
            { from: `${departureName}机场`, to: `${destinationCity}机场`, type: '航班' },
            { from: `${destinationCity}机场`, to: firstLocation.name, type: '地面交通' }
          ]
        })
      } else {
        // 公共交通/高铁 - 需要中转（出发地 → 火车站 → 目的地火车站 → 景点）
        const trainQueryUrl = `https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=${encodeURIComponent(departureName)}&ts=${encodeURIComponent(destinationCity)}&date=${preferences.departureDate ? new Date(preferences.departureDate).toISOString().split('T')[0] : ''}`
        
        if (directDistance > 100) {
          // 长距离使用高铁
          resolve({
            type: '高铁（需填写）',
            icon: '🚄',
            duration: `约${Math.ceil(directDistance / 200 * 60)}分钟`,
            distance: `${directDistance.toFixed(0)}km`,
            cost: Math.ceil(directDistance * 0.5),
            from: `${departureName}`,
            to: `${destinationCity}`,
            isDeparture: true,
            isManual: true,
            queryUrl: trainQueryUrl,
            note: '请点击填写车次信息（出发地 → 火车站 → 火车站 → 景点）',
            segments: [
              { from: departureName, to: `${departureName}站`, type: '地面交通' },
              { from: `${departureName}站`, to: `${destinationCity}站`, type: '高铁' },
              { from: `${destinationCity}站`, to: firstLocation.name, type: '地面交通' }
            ]
          })
        } else {
          // 短距离使用公交/地铁
          const transfer = new AMap.Transfer({
            city: destinationCity,
            policy: 0
          })
          
          transfer.search(departureCoords, destCoords, (status: string, result: any) => {
            if (status === 'complete' && result.plans && result.plans.length > 0) {
              const plan = result.plans[0]
              resolve({
                type: '公交/地铁',
                icon: '🚇',
                duration: `${Math.ceil(plan.time / 60)}分钟`,
                distance: `${(plan.distance / 1000).toFixed(1)}km`,
                cost: 10,
                from: departureName,
                to: firstLocation.name,
                isDeparture: true,
                note: '市内公共交通直达'
              })
            } else {
              resolve(getFallbackDepartureTransport(departureName, firstLocation, mode))
            }
          })
        }
      }
      
      // 超时保护
      setTimeout(() => {
        resolve(getFallbackDepartureTransport(departureName, firstLocation, mode))
      }, 5000)
    })
  } catch (error) {
    console.error('获取出发地交通信息失败:', error)
    return getFallbackDepartureTransport(departureName, firstLocation, mode)
  }
}

// 搜索城市中心坐标（使用Web服务API Key）
async function searchCityCenter(cityName: string) {
  try {
    const response = await fetch(
      `https://restapi.amap.com/v3/config/district?keywords=${cityName}&subdistrict=0&key=REDACTED_API_KEYf`
    )
    const data = await response.json()
    
    if (data.status === '1' && data.districts && data.districts.length > 0) {
      const center = data.districts[0].center.split(',')
      console.log(`城市中心坐标 ${cityName}:`, center)
      return [parseFloat(center[0]), parseFloat(center[1])]
    } else {
      console.warn(`未找到城市: ${cityName}`)
    }
  } catch (error) {
    console.error('搜索城市中心失败:', error)
  }
  return null
}

// 备用出发地交通信息
function getFallbackDepartureTransport(departureName: string, firstLocation: any, mode: string) {
  const fallbackData: any = {
    driving: {
      type: '自驾',
      icon: '🚗',
      duration: '预计根据实际路况',
      cost: 150,
      distance: '未知'
    },
    flying: {
      type: '飞机',
      icon: '✈️',
      duration: '预计根据航班',
      cost: 500,
      distance: '未知'
    },
    transit: {
      type: '高铁/动车',
      icon: '🚄',
      duration: '预计根据班次',
      cost: 200,
      distance: '未知'
    }
  }
  
  const data = fallbackData[mode] || fallbackData.transit
  
  return {
    ...data,
    from: `${departureName}`,
    to: firstLocation.name,
    isDeparture: true
  }
}

// 格式化出发时间
function formatDepartureTime() {
  if (!preferences.departureDate) return ''
  const date = new Date(preferences.departureDate)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 获取某一天的实际日期字符串（含星期）
function getDayDateString(dayNumber: number) {
  if (!preferences.departureDate) return ''
  
  try {
    const departDate = new Date(preferences.departureDate)
    // dayNumber是从1开始的，所以要减1
    const targetDate = new Date(departDate)
    targetDate.setDate(departDate.getDate() + dayNumber - 1)
    
    const month = targetDate.getMonth() + 1
    const date = targetDate.getDate()
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const weekday = weekdays[targetDate.getDay()]
    
    return `${month}月${date}日 星期${weekday}`
  } catch (error) {
    console.error('计算日期失败:', error)
    return ''
  }
}

// 获取上一天的住宿
function getPreviousDayHotel(day: number) {
  return pendingItems.value.find(item => item.day === day && item.locationType === 'hotel')
}

// 生成自动交通信息（调用高德API获取真实数据，参考AI建议）
async function generateAutoTransport(from: any, to: any, day: number) {
  if (!from || !to || !from.lng || !from.lat || !to.lng || !to.lat) {
    return {
      type: '未知',
      icon: '🚗',
      duration: '未知',
      cost: 0,
      from: from.name,
      to: to.name,
      isLoading: true
    }
  }
  
  const distance = calculateDistance(from.lng, from.lat, to.lng, to.lat)
  const AMap = (window as any).AMap
  
  // 检查AI是否有交通建议
  const daySchedule = itinerary.value?.daily_schedule?.find((d: any) => d.day === day)
  const aiSuggestions = daySchedule?.ai_transport_suggestions || []
  
  // 查找AI对这两个地点的交通建议
  let aiSuggestion = null
  for (const suggestion of aiSuggestions) {
    if (suggestion.from_location.includes(from.name) && suggestion.to_location.includes(to.name)) {
      aiSuggestion = suggestion
      console.log(`使用AI建议的交通方式: ${suggestion.type} (${from.name} → ${to.name})`)
      break
    }
  }
  
  // 优先使用AI建议的交通方式，否则根据距离判断
  let preferredMode = null
  if (aiSuggestion) {
    const aiType = aiSuggestion.type
    if (aiType.includes('步行')) preferredMode = 'walking'
    else if (aiType.includes('地铁') || aiType.includes('公交')) preferredMode = 'transit'
    else if (aiType.includes('出租') || aiType.includes('驾车')) preferredMode = 'driving'
  }
  
  // 返回一个Promise，异步获取交通信息
  return new Promise((resolve) => {
    // 确定使用的交通方式（优化：防止过长路段使用步行）
    const mode = preferredMode || (distance < 1.5 ? 'walking' : distance < 10 ? 'transit' : 'driving')
    
    if (mode === 'walking') {
      // 步行
      const walking = new AMap.Walking()
      walking.search([from.lng, from.lat], [to.lng, to.lat], (status: string, result: any) => {
        if (status === 'complete' && result.routes && result.routes.length > 0) {
          const route = result.routes[0]
          const aiTips = aiSuggestion?.tips || ''
          resolve({
            type: '步行',
            icon: '🚶',
            duration: `${Math.ceil(route.time / 60)}分钟`,
            distance: `${(route.distance / 1000).toFixed(1)}km`,
            cost: 0,
            from: from.name,
            to: to.name,
            aiTips: aiTips  // AI的交通建议
          })
        } else {
          resolve(getFallbackTransport(from, to, '步行'))
        }
      })
    } else if (distance < 10) {
      // 公交/地铁
      const transfer = new AMap.Transfer({
        city: itinerary.value?.destination || '北京',
        policy: 0  // 0: 最快捷模式
      })
      
      transfer.search([from.lng, from.lat], [to.lng, to.lat], (status: string, result: any) => {
        if (status === 'complete' && result.plans && result.plans.length > 0) {
          const plan = result.plans[0]
          const segments = plan.segments || []
          
          // 提取换乘信息
          const routes: string[] = []
          let totalCost = 0
          
          segments.forEach((seg: any) => {
            if (seg.transit_mode === 'SUBWAY') {
              routes.push(`地铁${seg.transit.name}`)
              totalCost += 3
            } else if (seg.transit_mode === 'BUS') {
              routes.push(`${seg.transit.name}`)
              totalCost += 2
            }
          })
          
          // 如果AI有建议且有tips，添加到结果中
          const aiTips = aiSuggestion?.tips || ''
          
          resolve({
            type: routes.length > 0 ? (routes[0].includes('地铁') ? '地铁' : '公交') : '公交',
            icon: routes.length > 0 ? (routes[0].includes('地铁') ? '🚇' : '🚌') : '🚌',
            duration: `${Math.ceil(plan.time / 60)}分钟`,
            distance: `${(plan.distance / 1000).toFixed(1)}km`,
            cost: totalCost || Math.ceil(distance * 0.5),
            route: routes.join(' → '),
            from: from.name,
            to: to.name,
            aiTips: aiTips  // AI的交通建议
          })
        } else {
          resolve(getFallbackTransport(from, to, '公交'))
        }
      })
    } else {
      // 驾车
      const driving = new AMap.Driving({
        policy: 0  // 0: 最快捷模式
      })
      
      driving.search([from.lng, from.lat], [to.lng, to.lat], (status: string, result: any) => {
        if (status === 'complete' && result.routes && result.routes.length > 0) {
          const route = result.routes[0]
          const aiTips = aiSuggestion?.tips || ''
          resolve({
            type: '出租车',
            icon: '🚕',
            duration: `${Math.ceil(route.time / 60)}分钟`,
            distance: `${(route.distance / 1000).toFixed(1)}km`,
            cost: calculateTaxiCost(route.distance / 1000),  // 使用真实出租车计价
            from: from.name,
            to: to.name,
            aiTips: aiTips  // AI的交通建议
          })
        } else {
          resolve(getFallbackTransport(from, to, '出租车'))
        }
      })
    }
    
    // 超时保护
    setTimeout(() => {
      resolve(getFallbackTransport(from, to, '公交'))
    }, 5000)
  })
}

// 备用交通信息（API调用失败时使用）
function getFallbackTransport(from: any, to: any, type: string) {
  const distance = from.lng && from.lat && to.lng && to.lat 
    ? calculateDistance(from.lng, from.lat, to.lng, to.lat) 
    : 1
  
  // 根据类型和距离做更准确的估算
  let duration = 0
  let cost = 0
  
  if (type === '步行') {
    duration = Math.ceil(distance * 15)  // 步行约4km/h
    cost = 0
  } else if (type === '公交' || type === '地铁') {
    duration = Math.ceil(distance * 3)  // 公交/地铁约20km/h
    cost = distance < 5 ? 2 : 5
  } else {
    // 出租车/驾车
    duration = Math.ceil(distance * 2)  // 驾车约30km/h（城市）
    cost = Math.ceil(distance * 3) + 10
  }
    
  return {
    type: type,
    icon: getTransportIcon(type),
    duration: `约${duration}分钟`,
    distance: `${distance.toFixed(1)}km`,
    cost: cost,
    from: from.name,
    to: to.name,
    note: '(估算值，实际可能有差异)'
  }
}

// 获取某天的非景点项目（交通+住宿） - 已弃用，使用getDayLocations代替
// 此函数保留用于向后兼容
function getDayNonAttractionItems(day: any) {
  const items: any[] = []
  
  // 添加住宿
  if (day.hotel) {
    items.push({
      type: 'hotel',
      id: `hotel-${day.day}`,
      ...day.hotel
    })
  }
  
  return items
}

// 获取交通方式图标
function getTransportIcon(type: string) {
  const icons: any = {
    '步行': '🚶',
    '公交': '🚌',
    '地铁': '🚇',
    '出租车': '🚕',
    '网约车': '🚗',
    '高铁': '🚄',
    '飞机': '✈️'
  }
  return icons[type] || '🚗'
}

// 推测交通方式（已弃用，保留用于向后兼容）
function getTransportType(from: any, to: any) {
  console.warn('getTransportType已弃用，请使用generateAutoTransport获取真实交通信息')
  if (from.lng && from.lat && to.lng && to.lat) {
    const distance = calculateDistance(from.lng, from.lat, to.lng, to.lat)
    if (distance < 1) return '步行'
    if (distance < 3) return '公交'
    if (distance < 10) return '地铁'
    return '出租车'
  }
  return '公交'
}

// 估算交通费用（已弃用，保留用于向后兼容）
function estimateTransportCost(from: any, to: any) {
  console.warn('estimateTransportCost已弃用，请使用generateAutoTransport获取真实费用')
  if (from.lng && from.lat && to.lng && to.lat) {
    const distance = calculateDistance(from.lng, from.lat, to.lng, to.lat)
    if (distance < 1) return 0
    if (distance < 3) return 2
    if (distance < 10) return 5
    return Math.round(distance * 3)
  }
  return 5
}

// 计算出租车费用（基于真实计价规则）
function calculateTaxiCost(distance: number) {
  // 以北京为例：起步价14元/3公里，超出后每公里2.3元
  const basePrice = 14
  const baseDistance = 3
  const pricePerKm = 2.3
  
  if (distance <= baseDistance) {
    return basePrice
  } else {
    return Math.ceil(basePrice + (distance - baseDistance) * pricePerKm)
  }
}

// 计算两点距离（Haversine公式）
function calculateDistance(lng1: number, lat1: number, lng2: number, lat2: number) {
  const R = 6371 // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// 更新某天的所有地点（景点+住宿）- 增强版：自动重新计算路线
function updateDayLocations(day: number, newLocations: any[]) {
  console.log(`更新第${day}天地点:`, newLocations.length, '个')
  
  // 移除该天的旧地点
  pendingItems.value = pendingItems.value.filter(item => item.day !== day)
  
  // 添加新地点
  newLocations.forEach(loc => {
    loc.day = day
    pendingItems.value.push(loc)
  })
  
  // 同步回itinerary
  syncItemsToItinerary()
  recordChange()
  
  // 自动重新计算路线
  console.log(`第${day}天行程已变化，重新计算路线...`)
  recalculateRouteForDay(day)
}

// 某天行程变化（防抖处理）
let _dayChangeTimer: any = null
function onDayChange(day: number) {
  console.log(`第${day}天行程已变化`)
  
  // 同步数据
  syncItemsToItinerary()
  
  // 防抖：避免频繁更新
  if (_dayChangeTimer) {
    clearTimeout(_dayChangeTimer)
  }
  
  _dayChangeTimer = setTimeout(() => {
    updateMapView(false)  // 不自动调整视野
    ElMessage.success(`第${day}天行程已更新`)
  }, 500)
}

// 移除地点 - 增强版：自动重新计算路线
function removeLocation(id: string, day: number) {
  const index = pendingItems.value.findIndex(item => item.id === id)
  if (index > -1) {
    const item = pendingItems.value[index]
    const itemDay = item.day
    
    pendingItems.value.splice(index, 1)
    syncItemsToItinerary()
    recordChange()
    
    ElMessage.success(`已删除：${item.name}`)
    
    // 如果移除的是已分配的地点，重新计算该天的路线
    if (itemDay > 0) {
      console.log(`移除了第${itemDay}天的地点，重新计算路线`)
      recalculateRouteForDay(itemDay)
    } else {
      updateMapView(false)  // 删除项目后不调整视野
    }
  }
}

// 计算某天的总费用（优化：直接从pendingItems计算，避免触发交通生成）
function calculateDayCost(day: any) {
  let total = 0
  
  // 直接从pendingItems获取，不触发getDayLocations的交通生成
  const locations = pendingItems.value.filter(item => item.day === day.day)
  
  locations.forEach(loc => {
    if (loc.locationType === 'attraction') {
      total += loc.cost || 0
    } else if (loc.locationType === 'hotel') {
      total += loc.price_per_night || 0
    }
    
    // 添加交通费用（如果已生成）
    if (loc.autoTransport && !loc.autoTransport.isLoading) {
      total += loc.autoTransport.cost || 0
    }
  })
  
  return total
}

// 从pendingItems同步回itinerary
function syncItemsToItinerary() {
  if (!itinerary.value) return
  
  itinerary.value.daily_schedule.forEach((day: any) => {
    // 同步景点
    const dayAttractions = pendingItems.value
      .filter(item => item.day === day.day && item.locationType === 'attraction')
      .sort((a, b) => {
        // 按时间排序
        if (a.start_time && b.start_time) {
          return a.start_time.localeCompare(b.start_time)
        }
        return 0
      })
    
    day.attractions = dayAttractions
    
    // 同步住宿
    const dayHotel = pendingItems.value.find(
      item => item.day === day.day && item.locationType === 'hotel'
    )
    if (dayHotel) {
      day.hotel = dayHotel
    }
  })
}

// 拖拽结束后自动重新计算路线（增强版）
function onDragEnd(evt: any) {
  console.log('拖拽结束，记录变更', evt)
  recordChange()
  
  // 获取拖拽涉及的天数
  const affectedDays = new Set<number>()
  
  // 如果有from和to信息，添加这两天
  if (evt.from && evt.from.dataset && evt.from.dataset.day) {
    affectedDays.add(Number(evt.from.dataset.day))
  }
  if (evt.to && evt.to.dataset && evt.to.dataset.day) {
    affectedDays.add(Number(evt.to.dataset.day))
  }
  
  // 检查所有天的行程（确保完整性）
  itinerary.value?.daily_schedule?.forEach((day: any) => {
    const dayItems = pendingItems.value.filter(item => item.day === day.day)
    if (dayItems.length > 0) {
      affectedDays.add(day.day)
    }
  })
  
  // 删除day=0的项（待安排区域）
  affectedDays.delete(0)
  
  console.log(`拖拽影响了${affectedDays.size}天: [${Array.from(affectedDays).join(', ')}]`)
  
  // 延迟重新计算受影响天数的路线（批量处理）
  setTimeout(async () => {
    const days = Array.from(affectedDays).sort((a, b) => a - b)
    for (const day of days) {
      console.log(`⏳ 重新计算第${day}天的路线...`)
      await recalculateRouteForDay(day)
      // 添加延迟，避免同时发起过多API请求
      await new Promise(resolve => setTimeout(resolve, 300))
    }
    console.log('✅ 所有受影响天数的路线已更新')
  }, 500)
}

// 重新计算某天的路线（旧版保留，用于手动优化）
async function recalculateRoute(day: number) {
  console.log(`重新计算第${day}天的路线...`)
  
  ElMessage.info(`正在重新计算第${day}天的最优路线...`)
  
  // TODO: 调用TSP优化API
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  ElMessage.success(`第${day}天路线已优化！`)
  updateMapView(false)  // 优化后不调整视野
}

// 重新计算某天的路线并重新绘制（新版：自动触发）
async function recalculateRouteForDay(day: number) {
  try {
    // 1. 同步该天的行程数据到itinerary
    syncItemsToItinerary()
    
    // 2. 获取该天的所有景点
    const dayData = itinerary.value?.daily_schedule?.find((d: any) => d.day === day)
    if (!dayData) {
      console.log(`第${day}天没有数据`)
      return
    }
    
    const attractions = dayData.attractions || []
    
    if (attractions.length < 1) {
      console.log(`第${day}天没有景点，清除路线`)
      await redrawSingleDay(day)
      return
    }
    
    if (attractions.length < 2) {
      console.log(`第${day}天只有1个景点，无需计算路线`)
      await redrawSingleDay(day)
      return
    }
    
    console.log(`⏳ 开始重新计算第${day}天的${attractions.length}个景点路线...`)
    
    // 3. 清除旧的交通信息
    const dayLocations = pendingItems.value.filter(item => item.day === day)
    dayLocations.forEach(loc => {
      if (loc.locationType === 'attraction') {
        delete loc.autoTransport
        delete loc._transportGenerating
      }
    })
    
    // 4. 重新生成交通信息
    for (let i = 0; i < attractions.length - 1; i++) {
      const from = attractions[i]
      const to = attractions[i + 1]
      
      if (!from.lng || !from.lat || !to.lng || !to.lat) continue
      
      // 计算距离，选择交通方式
      const distance = calculateDistance(from.lng, from.lat, to.lng, to.lat)
      const mode = distance < 1.5 ? 'walking' : distance < 10 ? 'transit' : 'driving'
      
      // 调用高德API获取真实路线（这里简化处理，实际应该调用后端API）
      console.log(`  ${from.name} → ${to.name}: ${distance.toFixed(2)}km, ${mode}`)
    }
    
    // 5. 只重新绘制该天的路线（不影响其他天）
    await redrawSingleDay(day)
    
    console.log(`✅ 第${day}天路线已更新`)
  } catch (error) {
    console.error(`重新计算第${day}天路线失败:`, error)
  }
}

// 重新绘制单独某一天的路线（不影响其他天）
async function redrawSingleDay(day: number) {
  if (!map.value) return
  
  try {
    const AMap = (window as any).AMap
    
    // 1. 移除该天的旧路线和标记
    const dayColor = getDayColor(day)
    const oldPolylines = polylines.value.filter((p: any) => p._dayColor === dayColor)
    oldPolylines.forEach((p: any) => {
      map.value.remove(p)
    })
    polylines.value = polylines.value.filter((p: any) => p._dayColor !== dayColor)
    
    // 移除该天的路线信息标记（如果有标记的话）
    const oldMarkers = markers.value.filter((m: any) => m._dayColor === dayColor && m._isRouteInfo)
    oldMarkers.forEach((m: any) => {
      map.value.remove(m)
    })
    markers.value = markers.value.filter((m: any) => !(m._dayColor === dayColor && m._isRouteInfo))
    
    // 2. 获取该天的数据
    const dayData = itinerary.value?.daily_schedule?.find((d: any) => d.day === day)
    if (!dayData || !dayData.attractions || dayData.attractions.length === 0) {
      console.log(`第${day}天没有景点，跳过绘制`)
      return
    }
    
    // 3. 重新绘制该天的路线
    await drawDayRoute(dayData, AMap)
    
    console.log(`第${day}天路线重新绘制完成`)
  } catch (error) {
    console.error(`重新绘制第${day}天路线失败:`, error)
  }
}

// 选择项目
function selectItem(item: any) {
  selectedItem.value = item
  if (item.lng && item.lat && map.value) {
    map.value.setZoomAndCenter(15, [item.lng, item.lat])
  }
}

// 更新待安排区域
function updatePendingItems(newItems: any[]) {
  // 移除所有未分配的
  pendingItems.value = pendingItems.value.filter(item => item.day && item.day > 0)
  // 添加新的未分配项
  newItems.forEach(item => {
    item.day = 0
    pendingItems.value.push(item)
  })
  recordChange()
}

// 移除项目
function removeItem(id: string) {
  const index = pendingItems.value.findIndex(item => item.id === id)
  if (index > -1) {
    const item = pendingItems.value[index]
    pendingItems.value.splice(index, 1)
    
    // 如果是已分配的景点，同步回itinerary
    if (item.day > 0) {
      syncItemsToItinerary()
      recalculateRoute(item.day)
    }
    
    recordChange()
  }
}

// 搜索景点（使用高德输入提示API）
async function performSearch() {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  
  // 自动设置搜索城市
  if (!searchCity.value) {
    searchCity.value = selectedDestinations.value[0] || itinerary.value?.destination || '北京'
  }
  
  searching.value = true
  try {
    console.log('搜索关键词:', searchKeyword.value, '城市:', searchCity.value)
    
    // 使用POI搜索v5 API（返回完整信息包括评分、费用、营业时间）
    const results = await searchAttractions({
      city: searchCity.value,
      keyword: searchKeyword.value.trim(),
      types: searchCategory.value || undefined,
      limit: 20
    })
    
    // 转换为搜索结果格式
    searchResults.value = Array.isArray(results) ? results.map((r: any) => ({
      id: r.id || `poi-${Date.now()}-${Math.random()}`,
      name: r.name,
      address: r.address,
      district: r.adname,
      adcode: r.adcode,
      lng: r.lng,
      lat: r.lat,
      type: r.typecode || r.type,
      typecode: r.typecode,
      cost: r.cost || 0,
      rating: r.rating || 0,
      tel: r.tel || '',
      opentime: r.opentime || '',
      business_area: r.business_area || '',
      photos: r.photos || []
    })) : []
    
    console.log('搜索结果:', searchResults.value.length, '个')
    
    if (searchResults.value.length === 0) {
      ElMessage.info('未找到相关结果，请尝试其他关键词')
    }
  } catch (error: any) {
    console.error('搜索失败:', error)
    ElMessage.error(error.message || '搜索失败，请重试')
  } finally {
    searching.value = false
  }
}

// 获取搜索建议（使用高德输入提示API）
async function fetchSuggestions(queryString: string, cb: Function) {
  if (!queryString || queryString.trim().length < 2) {
    cb([])
    return
  }
  
  try {
    // 自动设置搜索城市
    if (!searchCity.value) {
      searchCity.value = selectedDestinations.value[0] || itinerary.value?.destination || '北京'
    }
    
    // 调用高德输入提示API
    const response: any = await getInputTips({
      keywords: queryString.trim(),
      city: searchCity.value,
      datatype: searchCategory.value ? 'poi' : 'all',
      citylimit: true
    })
    
    const tips = response.tips || []
    
    // 转换为autocomplete格式
    const suggestions = tips
      .filter((tip: any) => {
        // 如果有分类筛选，过滤结果
        if (searchCategory.value && tip.typecode) {
          return tip.typecode.startsWith(searchCategory.value.substring(0, 2))
        }
        return true
      })
      .map((tip: any) => {
        const location = tip.location ? tip.location.split(',') : [0, 0]
        return {
          value: tip.name,
          id: tip.id || `tip-${Date.now()}-${Math.random()}`,
          name: tip.name,
          address: tip.address || tip.district,
          district: tip.district,
          adcode: tip.adcode,
          lng: parseFloat(location[0]),
          lat: parseFloat(location[1]),
          type: tip.typecode || '',
          typecode: tip.typecode
        }
      })
      .slice(0, 10)
    
    console.log(`输入提示: "${queryString}" -> ${suggestions.length}个建议`)
    cb(suggestions)
  } catch (error) {
    console.error('获取建议失败:', error)
    cb([])
  }
}

// 选择建议项
function handleSuggestionSelect(item: any) {
  // 直接添加选中的项目
  addSearchResult(item)
}

// 获取标签类型
function getTagType(type: string) {
  if (!type) return 'info'
  const typeCode = type.split('|')[0]
  
  if (typeCode.startsWith('11')) return 'primary'  // 景点
  if (typeCode.startsWith('10')) return 'success'  // 酒店
  if (typeCode.startsWith('05')) return 'warning'  // 餐饮
  if (typeCode.startsWith('06')) return 'danger'   // 购物
  
  return 'info'
}

// 添加搜索结果到待安排区域
function addSearchResult(result: any) {
  // 检查是否已存在
  const exists = pendingItems.value.some(item => 
    item.name === result.name && item.address === result.address
  )
  
  if (exists) {
    ElMessage.warning('该地点已存在')
    return
  }
  
  // 判断类型
  let locationType = 'attraction'
  if (result.type && result.type.startsWith('10')) {
    locationType = 'hotel'  // 酒店类
  } else if (result.type && result.type.startsWith('05')) {
    locationType = 'restaurant'  // 餐饮类
  }
  
  // 添加到待安排区域（包含v5新字段）
  const newItem = {
    id: `search-${Date.now()}-${Math.random()}`,
    day: 0,  // 0表示待安排
    locationType: locationType,
    name: result.name,
    address: result.address || '',
    lng: result.lng || 0,
    lat: result.lat || 0,
    type: result.type || '',
    typecode: result.typecode || '',
    cost: result.cost || 0,
    rating: result.rating || 0,
    tel: result.tel || '',
    opentime: result.opentime || '',
    business_area: result.business_area || '',
    photos: result.photos || [],
    image: result.photos && result.photos.length > 0 ? result.photos[0] : generateAttractionImage(result.name),
    tips: `从搜索添加 - ${getTypeName(result.type)}${result.opentime ? ` | 营业时间：${result.opentime}` : ''}`,
    // 如果是酒店，添加酒店特有字段
    ...(locationType === 'hotel' ? {
      price_per_night: result.cost || 200,
      reason: '手动添加的酒店'
    } : {
      start_time: '09:00',
      duration_hours: 2
    })
  }
  
  pendingItems.value.push(newItem)
  showSearch.value = false
  ElMessage.success(`已添加：${result.name}`)
  recordChange()
}

// 获取类型图标
function getTypeIcon(type: string) {
  if (!type) return 'Location'
  const typeCode = type.split('|')[0]
  
  if (typeCode.startsWith('11')) return 'Place'  // 景点
  if (typeCode.startsWith('10')) return 'House'  // 酒店
  if (typeCode.startsWith('05')) return 'Food'   // 餐饮
  if (typeCode.startsWith('06')) return 'ShoppingCart'  // 购物
  if (typeCode.startsWith('07')) return 'Service'  // 服务
  
  return 'Location'
}

// 获取类型颜色
function getTypeColor(type: string) {
  if (!type) return '#909399'
  const typeCode = type.split('|')[0]
  
  if (typeCode.startsWith('11')) return '#409EFF'  // 景点-蓝色
  if (typeCode.startsWith('10')) return '#67C23A'  // 酒店-绿色
  if (typeCode.startsWith('05')) return '#E6A23C'  // 餐饮-橙色
  if (typeCode.startsWith('06')) return '#F56C6C'  // 购物-红色
  if (typeCode.startsWith('07')) return '#909399'  // 服务-灰色
  
  return '#909399'
}

// 获取类型名称
function getTypeName(type: string) {
  if (!type) return '地点'
  const typeCode = type.split('|')[0]
  
  // 景点类型
  if (typeCode.startsWith('11')) {
    if (typeCode.startsWith('1101')) return '公园广场'
    if (typeCode.startsWith('1102')) return '风景名胜'
    if (typeCode.startsWith('1103')) return '文物古迹'
    if (typeCode.startsWith('1104')) return '教堂寺庙'
    return '景点'
  }
  
  // 住宿类型
  if (typeCode.startsWith('10')) return '酒店'
  
  // 餐饮类型
  if (typeCode.startsWith('05')) return '餐饮'
  
  // 购物类型
  if (typeCode.startsWith('06')) return '购物'
  
  // 生活服务
  if (typeCode.startsWith('07')) return '服务'
  
  return '地点'
}

// 智能优化
async function smartOptimize() {
  if (!itinerary.value) {
    ElMessage.warning('请先生成行程')
    return
  }
  
  optimizing.value = true
  ElMessage.info('正在使用TSP算法优化路线...')
  
  try {
    // TODO: 调用优化API
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('优化完成！')
  } catch (error) {
    ElMessage.error('优化失败')
  } finally {
    optimizing.value = false
  }
}

// 保存行程
function saveTrip() {
  ElMessage.success('保存功能开发中...')
}

// 撤销/重做
function recordChange() {
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(JSON.parse(JSON.stringify(pendingItems.value)))
  historyIndex.value++
  if (history.value.length > 50) {
    history.value.shift()
    historyIndex.value--
  }
}

function undo() {
  if (historyIndex.value > 0) {
    historyIndex.value--
    pendingItems.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    ElMessage.info('已撤销')
  }
}

function redo() {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    pendingItems.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    ElMessage.info('已重做')
  }
}

// 键盘快捷键
function handleKeyboard(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    e.preventDefault()
    undo()
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
    e.preventDefault()
    redo()
  }
}

// 更新地图
function updateMap() {
  // TODO: 实现地图更新
}

// 工具函数
function buildPreferencesInfo() {
  const parts = []
  if (preferences.companion !== '独自') parts.push(preferences.companion)
  if (preferences.styles.length) parts.push(preferences.styles.join('、'))
  parts.push(`节奏${preferences.pace}`)
  return parts.join('，')
}

function extractDestination(text: string) {
  const match = text.match(/去?([^\s，,]{2,})(旅|玩)/)
  return match ? match[1] : ''
}

function extractDays(text: string) {
  const match = text.match(/(\d+)\s*天/)
  return match ? parseInt(match[1]) : preferences.days
}

function extractBudget(text: string) {
  const match = text.match(/预算[：:¥]?\s*(\d+)/)
  if (match) return parseInt(match[1])
  return preferences.budget === 0 ? customBudget.value : preferences.budget
}

function formatMessage(content: string) {
  return content.replace(/\n/g, '<br>')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 图片加载错误处理
function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement
  const parent = target.closest('.location-card')
  const isHotel = parent?.classList.contains('hotel')
  
  // 替换为SVG占位图
  if (isHotel) {
    target.src = generateHotelImage('')
  } else {
    target.src = generateAttractionImage('')
  }
}

// 根据天气描述获取图标
function getWeatherIcon(weather: string) {
  const icons: any = {
    '晴': '☀️',
    '多云': '⛅',
    '阴': '☁️',
    '阵雨': '🌦️',
    '雷阵雨': '⛈️',
    '小雨': '🌧️',
    '中雨': '🌧️',
    '大雨': '🌧️',
    '暴雨': '⛈️',
    '雪': '❄️',
    '雾': '🌫️',
    '霾': '😷'
  }
  
  for (const key in icons) {
    if (weather.includes(key)) {
      return icons[key]
    }
  }
  
  return '🌤️'
}

// 批量DOM更新调度（优化渲染性能）
function scheduleDOMUpdate() {
  if (_domUpdateTimer) return
  
  _domUpdateTimer = requestAnimationFrame(() => {
    // 批量执行DOM更新
    _pendingDOMUpdates.forEach(fn => fn())
    _pendingDOMUpdates = []
    _domUpdateTimer = null
    scrollToBottom()
  })
}

// 打开火车票填写对话框
function openTrainDialog(element: any) {
  currentTransport.value = element
  
  // 如果已有信息，填充到表单
  if (element.autoTransport.trainNum) {
    trainForm.trainNum = element.autoTransport.trainNum
    trainForm.departStation = element.autoTransport.departStation || element.autoTransport.from
    trainForm.arrivalStation = element.autoTransport.arrivalStation || element.autoTransport.to
    trainForm.departTime = element.autoTransport.departTime || ''
    trainForm.arrivalTime = element.autoTransport.arrivalTime || ''
    trainForm.seatType = element.autoTransport.seatType || '二等座'
    trainForm.price = element.autoTransport.price || element.autoTransport.cost || 0
    trainForm.duration = element.autoTransport.actualDuration || element.autoTransport.duration || ''
  } else {
    // 预填充基本信息
    trainForm.departStation = element.autoTransport.from.replace('站', '')
    trainForm.arrivalStation = element.autoTransport.to.replace('站', '')
    trainForm.price = element.autoTransport.cost || 0
  }
  
  // 加载车站数据
  loadStationData()
  
  showTrainDialog.value = true
}

// 加载车站数据（from 12306）
async function loadStationData() {
  if (stationSuggestions.value.length > 0) {
    return  // 已加载
  }
  
  loadingStations.value = true
  try {
    const response = await fetch('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js')
    const text = await response.text()
    
    // 解析: var station_names ='@bjb|北京北|VAP|...'
    const match = text.match(/'(.+)'/)
    if (match) {
      const stationsStr = match[1]
      const stations = stationsStr.split('@')
      
      const stationNames: string[] = []
      stations.forEach(station => {
        if (!station) return
        const parts = station.split('|')
        if (parts.length >= 2) {
          stationNames.push(parts[1])  // 站名
        }
      })
      
      stationSuggestions.value = stationNames
      console.log(`加载了${stationNames.length}个车站`)
    }
  } catch (error) {
    console.error('加载车站数据失败:', error)
  } finally {
    loadingStations.value = false
  }
}

// 搜索车站（用于autocomplete）
function searchStations(queryString: string, cb: (results: any[]) => void) {
  if (!queryString) {
    cb([])
    return
  }
  
  const results = stationSuggestions.value
    .filter(station => 
      station.includes(queryString) || 
      station.toLowerCase().includes(queryString.toLowerCase())
    )
    .slice(0, 20)  // 最多20个结果
    .map(station => ({ value: station }))
  
  cb(results)
}

// 搜索机场（用于autocomplete）
function searchAirports(queryString: string, cb: (results: any[]) => void) {
  if (!queryString) {
    cb([])
    return
  }
  
  const results = searchAirportsByName(queryString)
    .map(airport => ({
      value: airport.name,
      label: `${airport.name} (${airport.iata}) - ${airport.city}`
    }))
  
  cb(results)
}

// 更新出发机场列表
function updateDepartAirports() {
  flightForm.departAirport = ''
}

// 更新到达机场列表
function updateArrivalAirports() {
  flightForm.arrivalAirport = ''
}

// 根据城市搜索机场
function searchAirportsByCity(cityName: string) {
  return airports.filter(airport => 
    airport.city.includes(cityName) || 
    airport.region.includes(cityName) ||
    cityName.includes(airport.city)
  )
}

// 打开航班填写对话框
function openFlightDialog(element: any) {
  currentTransport.value = element
  
  // 如果已有信息，填充到表单
  if (element.autoTransport.flightNum) {
    flightForm.flightNum = element.autoTransport.flightNum
    flightForm.departAirport = element.autoTransport.departAirport || element.autoTransport.from
    flightForm.arrivalAirport = element.autoTransport.arrivalAirport || element.autoTransport.to
    flightForm.departTime = element.autoTransport.departTime || ''
    flightForm.arrivalTime = element.autoTransport.arrivalTime || ''
    flightForm.cabinClass = element.autoTransport.cabinClass || '经济舱'
    flightForm.price = element.autoTransport.price || element.autoTransport.cost || 0
    flightForm.duration = element.autoTransport.actualDuration || element.autoTransport.duration || ''
    
    // 智能匹配省市
    const departAirport = airports.find(a => a.name === flightForm.departAirport)
    const arrivalAirport = airports.find(a => a.name === flightForm.arrivalAirport)
    if (departAirport) flightForm.departProvince = departAirport.region
    if (arrivalAirport) flightForm.arrivalProvince = arrivalAirport.region
  } else {
    // 预填充基本信息
    const departCity = element.autoTransport.from.replace('机场', '').replace('站', '')
    const arrivalCity = element.autoTransport.to.replace('机场', '').replace('站', '').replace('附近', '')
    
    // 尝试匹配机场和省市
    const departAirports = searchAirportsByCity(departCity)
    const arrivalAirports = searchAirportsByCity(arrivalCity)
    
    if (departAirports.length > 0) {
      flightForm.departProvince = departAirports[0].region
      flightForm.departAirport = departAirports[0].name
    }
    if (arrivalAirports.length > 0) {
      flightForm.arrivalProvince = arrivalAirports[0].region
      flightForm.arrivalAirport = arrivalAirports[0].name
    }
    
    flightForm.price = element.autoTransport.cost || 0
  }
  
  showFlightDialog.value = true
}

// 保存航班信息
function saveFlightInfo() {
  if (!currentTransport.value || !flightForm.flightNum) {
    ElMessage.warning('请至少填写航班号')
    return
  }
  
  // 计算飞行时长
  let durationStr = flightForm.duration
  if (!durationStr && flightForm.departTime && flightForm.arrivalTime) {
    const depart = new Date(`2000-01-01 ${flightForm.departTime}`)
    const arrival = new Date(`2000-01-01 ${flightForm.arrivalTime}`)
    const diffMinutes = Math.floor((arrival.getTime() - depart.getTime()) / 60000)
    const hours = Math.floor(diffMinutes / 60)
    const minutes = diffMinutes % 60
    durationStr = hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
  }
  
  // 更新交通信息
  const transport = currentTransport.value.autoTransport
  transport.flightNum = flightForm.flightNum
  transport.departAirport = flightForm.departAirport
  transport.arrivalAirport = flightForm.arrivalAirport
  transport.departTime = flightForm.departTime ? 
    (typeof flightForm.departTime === 'string' ? flightForm.departTime : 
     `${flightForm.departTime.getHours().toString().padStart(2, '0')}:${flightForm.departTime.getMinutes().toString().padStart(2, '0')}`) : ''
  transport.arrivalTime = flightForm.arrivalTime ?
    (typeof flightForm.arrivalTime === 'string' ? flightForm.arrivalTime :
     `${flightForm.arrivalTime.getHours().toString().padStart(2, '0')}:${flightForm.arrivalTime.getMinutes().toString().padStart(2, '0')}`) : ''
  transport.cabinClass = flightForm.cabinClass
  transport.price = flightForm.price
  transport.actualDuration = durationStr
  transport.cost = flightForm.price  // 更新费用
  
  // 更新显示信息
  if (transport.flightNum) {
    transport.type = `${transport.flightNum} ${flightForm.cabinClass}`
    if (durationStr) {
      transport.duration = durationStr
    }
  }
  
  showFlightDialog.value = false
  ElMessage.success('航班信息已保存')
  
  // 更新地图 - 绘制飞行路线
  nextTick(() => {
    updateMapView(false)  // 不自动调整视野
    // 如果有机场信息，绘制飞行路线
    if (transport.departAirport && transport.arrivalAirport) {
      drawFlightRoute(transport)
    }
  })
}

// 绘制飞行路线
async function drawFlightRoute(transport: any) {
  if (!map.value) return
  
  try {
    // 搜索出发和到达机场的坐标
    const departCity = transport.departAirport.split('机场')[0].replace(/国际|机场/g, '')
    const arrivalCity = transport.arrivalAirport.split('机场')[0].replace(/国际|机场/g, '')
    
    const departCoords = await searchCityCenter(departCity)
    const arrivalCoords = await searchCityCenter(arrivalCity)
    
    if (!departCoords || !arrivalCoords) {
      console.warn('无法获取机场坐标，跳过绘制飞行路线')
      return
    }
    
    const AMap = (window as any).AMap
    
    // 清除之前的飞行路线
    const oldFlightLine = polylines.value.find(p => p.getExtData && p.getExtData().type === 'flight')
    if (oldFlightLine) {
      map.value.remove(oldFlightLine)
      const index = polylines.value.indexOf(oldFlightLine)
      if (index > -1) {
        polylines.value.splice(index, 1)
      }
    }
    
    // 绘制飞行路线（使用特殊样式 - 蓝色虚线）
    const flightLine = new AMap.Polyline({
      path: [departCoords, arrivalCoords],
      strokeColor: '#2196f3',  // 蓝色
      strokeWeight: 5,
      strokeOpacity: 0.7,
      strokeStyle: 'dashed',  // 虚线
      strokeDasharray: [10, 10],
      lineJoin: 'round',
      lineCap: 'round',
      showDir: true,
      dirColor: '#2196f3',
      zIndex: 110  // 高于火车路线
    })
    
    flightLine.setExtData({ type: 'flight', transport })
    
    map.value.add(flightLine)
    polylines.value.push(flightLine)
    
    // 添加机场标记（使用飞机图标）
    const departMarker = new AMap.Marker({
      position: departCoords,
      content: '<div style="background: #2196f3; color: white; padding: 4px 8px; border-radius: 4px; font-size: 16px;">✈️</div>',
      offset: new AMap.Pixel(-16, -16),
      title: `${transport.departAirport}\n${transport.departTime || ''}`
    })
    
    const arrivalMarker = new AMap.Marker({
      position: arrivalCoords,
      content: '<div style="background: #4caf50; color: white; padding: 4px 8px; border-radius: 4px; font-size: 16px;">🛬</div>',
      offset: new AMap.Pixel(-16, -16),
      title: `${transport.arrivalAirport}\n${transport.arrivalTime || ''}`
    })
    
    map.value.add([departMarker, arrivalMarker])
    markers.value.push(departMarker, arrivalMarker)
    
    // 自动调整视野（延迟执行）
    setTimeout(() => {
      if (map.value) {
        map.value.setFitView([flightLine, departMarker, arrivalMarker], false, [60, 60, 60, 60])
      }
    }, 300)
    
    console.log('飞行路线绘制完成')
    
  } catch (error) {
    console.error('绘制飞行路线失败:', error)
  }
}

// 重置航班表单
function resetFlightForm() {
  flightForm.flightNum = ''
  flightForm.departProvince = ''
  flightForm.departAirport = ''
  flightForm.arrivalProvince = ''
  flightForm.arrivalAirport = ''
  flightForm.departTime = ''
  flightForm.arrivalTime = ''
  flightForm.cabinClass = '经济舱'
  flightForm.price = 0
  flightForm.duration = ''
  currentTransport.value = null
}


// 保存火车票信息
function saveTrainInfo() {
  if (!currentTransport.value || !trainForm.trainNum) {
    ElMessage.warning('请至少填写车次号')
    return
  }
  
  // 计算时长
  let durationStr = trainForm.duration
  if (!durationStr && trainForm.departTime && trainForm.arrivalTime) {
    const depart = new Date(`2000-01-01 ${trainForm.departTime}`)
    const arrival = new Date(`2000-01-01 ${trainForm.arrivalTime}`)
    const diffMinutes = Math.floor((arrival.getTime() - depart.getTime()) / 60000)
    const hours = Math.floor(diffMinutes / 60)
    const minutes = diffMinutes % 60
    durationStr = hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
  }
  
  // 更新交通信息
  const transport = currentTransport.value.autoTransport
  transport.trainNum = trainForm.trainNum
  transport.departStation = trainForm.departStation
  transport.arrivalStation = trainForm.arrivalStation
  transport.departTime = trainForm.departTime ? 
    (typeof trainForm.departTime === 'string' ? trainForm.departTime : 
     `${trainForm.departTime.getHours().toString().padStart(2, '0')}:${trainForm.departTime.getMinutes().toString().padStart(2, '0')}`) : ''
  transport.arrivalTime = trainForm.arrivalTime ?
    (typeof trainForm.arrivalTime === 'string' ? trainForm.arrivalTime :
     `${trainForm.arrivalTime.getHours().toString().padStart(2, '0')}:${trainForm.arrivalTime.getMinutes().toString().padStart(2, '0')}`) : ''
  transport.seatType = trainForm.seatType
  transport.price = trainForm.price
  transport.actualDuration = durationStr
  transport.cost = trainForm.price  // 更新费用
  
  // 更新显示信息
  if (transport.trainNum) {
    transport.type = `${transport.trainNum} ${trainForm.seatType}`
    if (durationStr) {
      transport.duration = durationStr
    }
  }
  
  showTrainDialog.value = false
  ElMessage.success('火车票信息已保存')
  
  // 更新地图 - 绘制出发地到目的地的火车路线
  nextTick(() => {
    updateMapView(false)  // 不自动调整视野
    // 如果有车站坐标，绘制火车路线
    if (transport.departStation && transport.arrivalStation) {
      drawTrainRoute(transport)
    }
  })
}

// 绘制火车路线（出发城市到目的地城市）
async function drawTrainRoute(transport: any) {
  if (!map.value) return
  
  try {
    // 获取出发站和到达站的坐标
    const departCoords = await searchCityCenter(transport.departStation.replace('站', '').replace('南', '').replace('北', '').replace('东', '').replace('西', '').replace('虹桥', ''))
    const arrivalCoords = await searchCityCenter(transport.arrivalStation.replace('站', '').replace('南', '').replace('北', '').replace('东', '').replace('西', '').replace('虹桥', ''))
    
    if (!departCoords || !arrivalCoords) {
      console.warn('无法获取车站坐标，跳过绘制火车路线')
      return
    }
    
    const AMap = (window as any).AMap
    
    // 清除之前的火车路线
    const oldTrainLine = polylines.value.find(p => p.getExtData && p.getExtData().type === 'train')
    if (oldTrainLine) {
      map.value.remove(oldTrainLine)
      const index = polylines.value.indexOf(oldTrainLine)
      if (index > -1) {
        polylines.value.splice(index, 1)
      }
    }
    
    // 绘制火车路线（使用特殊样式）
    const trainLine = new AMap.Polyline({
      path: [departCoords, arrivalCoords],
      strokeColor: '#ff6b6b',  // 红色
      strokeWeight: 6,
      strokeOpacity: 0.8,
      strokeStyle: 'solid',
      lineJoin: 'round',
      lineCap: 'round',
      showDir: true,
      dirColor: '#ff6b6b',
      zIndex: 100
    })
    
    trainLine.setExtData({ type: 'train', transport })
    
    map.value.add(trainLine)
    polylines.value.push(trainLine)
    
    // 添加出发站和到达站的标记
    const departMarker = new AMap.Marker({
      position: departCoords,
      icon: new AMap.Icon({
        size: new AMap.Size(40, 50),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-marker.png',
        imageSize: new AMap.Size(40, 50)
      }),
      title: `${transport.departStation}\n${transport.departTime || ''}`
    })
    
    const arrivalMarker = new AMap.Marker({
      position: arrivalCoords,
      icon: new AMap.Icon({
        size: new AMap.Size(40, 50),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/dir-marker.png',
        imageSize: new AMap.Size(40, 50)
      }),
      title: `${transport.arrivalStation}\n${transport.arrivalTime || ''}`
    })
    
    map.value.add([departMarker, arrivalMarker])
    markers.value.push(departMarker, arrivalMarker)
    
    // 自动调整视野包含火车路线（延迟执行）
    setTimeout(() => {
      if (map.value) {
        map.value.setFitView([trainLine, departMarker, arrivalMarker], false, [60, 60, 60, 60])
      }
    }, 300)
    
    console.log('火车路线绘制完成')
    
  } catch (error) {
    console.error('绘制火车路线失败:', error)
  }
}

// 重置表单
function resetTrainForm() {
  trainForm.trainNum = ''
  trainForm.departStation = ''
  trainForm.arrivalStation = ''
  trainForm.departTime = ''
  trainForm.arrivalTime = ''
  trainForm.seatType = '二等座'
  trainForm.price = 0
  trainForm.duration = ''
  currentTransport.value = null
}
</script>

<style scoped>
.ultimate-planner {
  display: flex;
  height: calc(100vh - 60px);
  background: #f5f5f5;
}

/* 左侧栏 (25%) */
.left-sidebar {
  background: white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  min-width: 280px;
  max-width: 350px;
  height: calc(100vh - 60px);  /* 固定高度 */
  overflow: hidden;  /* 防止溢出 */
}

.sidebar-header {
  padding: 14px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fafafa;
  flex-shrink: 0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.preferences-collapse {
  border: none;
  flex-shrink: 0;
}

.preferences-collapse :deep(.el-collapse-item__header) {
  padding: 0 16px;
  height: 40px;
  line-height: 40px;
  font-size: 13px;
  background: #fafafa;
}

.preferences-collapse :deep(.el-collapse-item__content) {
  padding: 12px 16px;
  background: #fafafa;
  max-height: 60vh;
  overflow-y: auto;
}

.pref-section {
  margin-bottom: 12px;
}

.pref-title {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #606266;
}

.destinations-list {
  min-height: 32px;
  padding: 6px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.pref-section :deep(.el-radio-group),
.pref-section :deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* 对话区 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  scroll-behavior: smooth;
  max-height: calc(100vh - 60px - 50px - 40px - 80px);  /* 减去header、偏好设置、输入框的高度 */
}

.message {
  margin-bottom: 10px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user .message-content {
  background: #409eff;
  color: white;
  margin-left: 30px;
  max-width: calc(100% - 30px);
}

.message.assistant .message-content {
  background: #f4f4f5;
  margin-right: 30px;
  max-width: calc(100% - 30px);
  width: 100%;  /* 占满可用空间，防止宽度抖动 */
  box-sizing: border-box;
}

.message-content {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
  min-width: 200px;  /* 最小宽度 */
  width: fit-content;  /* 自适应内容 */
}

.message-content pre {
  white-space: pre-wrap !important;
  word-break: break-all !important;
  overflow-x: hidden !important;
  max-width: 100% !important;
}

.message-content :deep(.success-msg) {
  background: #f0f9ff;
  border-left: 3px solid #67c23a;
  padding: 10px;
  border-radius: 4px;
}

.message-content :deep(.error-msg) {
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
  padding: 10px;
  border-radius: 4px;
}

.message-content :deep(.thinking-item) {
  font-size: 12px;
  color: #909399;
  padding: 6px 10px;
  margin: 4px 0;
  background: #f0f0f0;
  border-left: 3px solid #909399;
  border-radius: 4px;
  font-style: italic;
}

.message-content :deep(.deepseek-item) {
  font-size: 12px;
  color: #6366f1;
  padding: 6px 10px;
  margin: 4px 0;
  background: linear-gradient(90deg, #eef2ff 0%, #fafafa 100%);
  border-left: 3px solid #6366f1;
  border-radius: 4px;
  font-weight: 500;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

/* 折叠的思考内容 */
.message-content :deep(.thinking-collapsed) {
  margin: 8px 0 16px 0;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: #f9fafb;
  overflow: hidden;
}

.message-content :deep(.thinking-collapsed summary) {
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
  font-size: 13px;
  color: #4b5563;
  font-weight: 500;
  list-style: none;
  transition: all 0.2s;
}

.message-content :deep(.thinking-collapsed summary)::-webkit-details-marker {
  display: none;
}

.message-content :deep(.thinking-collapsed summary)::before {
  content: '▶';
  display: inline-block;
  margin-right: 6px;
  transition: transform 0.2s;
}

.message-content :deep(.thinking-collapsed[open] summary)::before {
  transform: rotate(90deg);
}

.message-content :deep(.thinking-collapsed summary):hover {
  background: #f3f4f6;
}

.message-content :deep(.thinking-collapsed[open] summary) {
  border-bottom: 1px solid #e5e7eb;
  background: #f3f4f6;
}

.message-content :deep(.main-content) {
  margin-top: 4px;
}

.message-content :deep(.deepseek-stream) {
  padding: 12px;
  margin: 8px 0;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  width: 100%;  /* 固定宽度，不随内容变化 */
  box-sizing: border-box;
}

.message-content :deep(.deepseek-stream pre) {
  margin: 8px 0 0 0;
  padding: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 11px;
  line-height: 1.4;
}

.message-content :deep(.progress-detail) {
  font-size: 12px;
  color: #f59e0b;
  padding: 6px 10px;
  margin: 4px 0;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 4px;
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message-content :deep(.status-item) {
  font-size: 12px;
  color: #409eff;
  padding: 6px 10px;
  margin: 4px 0;
  background: #ecf5ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}

/* Agent启动 */
.message-content :deep(.agent-start) {
  font-size: 13px;
  color: #6366f1;
  padding: 10px 14px;
  margin: 8px 0;
  background: linear-gradient(90deg, #eef2ff 0%, #fafafa 100%);
  border-left: 4px solid #6366f1;
  border-radius: 6px;
  font-weight: 600;
}

/* 工具调用开始 */
.message-content :deep(.tool-call) {
  font-size: 12px;
  color: #f59e0b;
  padding: 10px 14px;
  margin: 8px 0;
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
  border-radius: 6px;
  font-weight: 500;
}

.message-content :deep(.tool-call-header) {
  margin-bottom: 8px;
  font-weight: 600;
}

.message-content :deep(.tool-input) {
  background: #fef3c7;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  color: #92400e;
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 工具调用完成 */
.message-content :deep(.tool-result) {
  font-size: 11px;
  color: #10b981;
  padding: 10px 14px;
  margin: 8px 0;
  background: #ecfdf5;
  border-left: 3px solid #10b981;
  border-radius: 6px;
}

.message-content :deep(.tool-result-header) {
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 12px;
}

.message-content :deep(.tool-output) {
  background: #d1fae5;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  color: #065f46;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* AI最终回复 */
.message-content :deep(.ai-reply) {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.8;
  margin: 12px 0;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

/* 最终回复 */
.message-content :deep(.final-reply) {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.8;
  margin: 12px 0;
  padding: 14px;
  background: #f0fdf4;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.chat-input {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
}

.quick-settings {
  padding: 8px 12px;
  background: linear-gradient(90deg, #f5f7fa 0%, #e8f4ff 100%);
  border-radius: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.quick-settings:hover {
  background: linear-gradient(90deg, #e8f4ff 0%, #d9ecff 100%);
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

/* 中间内容区 (35%) */
.center-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #fafafa;
  height: calc(100vh - 60px);  /* 固定高度 */
  max-height: calc(100vh - 60px);  /* 最大高度 */
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  background: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  position: sticky;
  top: 0;
  z-index: 10;
}

.content-header h2 {
  margin: 0 0 8px 0;
  font-size: 22px;
}

.quick-stats {
  display: flex;
  gap: 8px;
}

.itinerary-editor {
  max-width: 800px;
  margin: 0 auto;
}

.pending-zone {
  background: white;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
  border: 2px dashed #e4e7ed;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
}

.items-container {
  min-height: 80px;
}

.day-schedule {
  background: white;
  border-radius: 16px;
  padding: 0;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  overflow: hidden;
}

/* 天标题卡片 */
.day-title-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.day-title-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.day-title-card h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.day-title-card .day-date {
  font-size: 14px;
  font-weight: 400;
  opacity: 0.95;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 10px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.day-title-card .day-theme {
  font-size: 13px;
  font-weight: 400;
  opacity: 0.9;
  display: inline-block;
  padding: 2px 0;
}

.day-stats {
  display: flex;
  gap: 8px;
}

/* 完整时间线 */
.full-timeline {
  padding: 20px;
}

.locations-draggable {
  min-height: 100px;
}

.day-attractions {
  min-height: 100px;
  margin-bottom: 12px;
}

.day-attractions-draggable {
  min-height: 60px;
  margin-bottom: 12px;
}

.timeline-item.draggable {
  cursor: move !important;
}

.timeline-item.draggable:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}

.timeline-item.draggable .timeline-marker {
  cursor: grab;
}

.timeline-item.draggable .timeline-marker:active {
  cursor: grabbing;
}

/* 时间线样式 */
.timeline-container {
  position: relative;
  padding-left: 60px;
}

.timeline-container-simple {
  position: relative;
  padding-left: 20px;
  margin-top: 12px;
}

/* 自动交通线 */
.auto-transport {
  padding: 8px 0;
  margin: -8px 0 8px 0;
}

.transport-line {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: linear-gradient(90deg, #f0f9ff 0%, transparent 100%);
  border-left: 3px solid #67c23a;
  border-radius: 0 8px 8px 0;
  transition: all 0.3s;
}

.transport-line:hover {
  background: linear-gradient(90deg, #e3f4ff 0%, transparent 100%);
  transform: translateX(2px);
}

/* 出发地交通特殊样式 */
.auto-transport:has(.transport-departure) .transport-line {
  background: linear-gradient(90deg, #fff7e6 0%, transparent 100%);
  border-left: 4px solid #fa8c16;
  box-shadow: 0 2px 8px rgba(250, 140, 22, 0.15);
}

.auto-transport:has(.transport-departure) .transport-line:hover {
  background: linear-gradient(90deg, #ffe7ba 0%, transparent 100%);
}

.transport-departure {
  display: flex;
  align-items: center;
  gap: 8px;
}

.transport-departure .transport-text {
  color: #52c41a;
  font-weight: 600;
}

.transport-icon {
  font-size: 20px;
}

.transport-text {
  font-size: 12px;
  color: #67c23a;
  font-weight: 500;
}

/* 地点卡片 */
.location-card {
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  cursor: move;
  transition: all 0.3s;
  position: relative;
  display: flex;
  gap: 12px;
}

.location-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transform: translateY(-3px);
  border-color: #409eff;
}

.location-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.location-card.attraction {
  border-left: 4px solid #409eff;
}

.location-card.hotel {
  border-left: 4px solid #e6a23c;
  background: #fef5e7;
}

.location-card.prev-hotel {
  opacity: 0.7;
  cursor: pointer;
  border-style: dashed;
}

.location-card.departure {
  border-left: 4px solid #52c41a;
  background: #f6ffed;
  cursor: default;
}

.location-card.departure .card-badge {
  background: #52c41a;
}

.card-badge {
  position: absolute;
  top: -10px;
  left: 12px;
  background: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.location-card.hotel .card-badge {
  background: #e6a23c;
}

.card-icon {
  font-size: 32px;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
}

.card-image {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}

.card-tips {
  font-size: 12px;
  color: #f56c6c;
  margin: 4px 0;
  background: #fef0f0;
  padding: 4px 8px;
  border-radius: 4px;
  line-height: 1.5;
}

.card-address {
  font-size: 11px;
  color: #909399;
  margin: 4px 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
}

.timeline-time {
  position: absolute;
  left: -60px;
  width: 50px;
  text-align: right;
  font-size: 11px;
  color: #909399;
  padding-top: 4px;
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-right: 12px;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
  transition: all 0.3s;
}

.timeline-item.draggable .timeline-marker:hover {
  transform: scale(1.2);
  background: #ecf5ff;
  border-color: #409eff;
}

.timeline-item.attraction .timeline-marker {
  border-color: #409eff;
  background: #ecf5ff;
}

.timeline-item.transport .timeline-marker {
  border-color: #67c23a;
  background: #f0f9ff;
  font-size: 14px;
}

.timeline-item.hotel .timeline-marker {
  border-color: #e6a23c;
  background: #fdf6ec;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  bottom: -24px;
  width: 2px;
  background: #e4e7ed;
  z-index: 1;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-content {
  flex: 1;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.timeline-content:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.timeline-item.attraction .timeline-content {
  border-left: 3px solid #409eff;
}

.timeline-item.hotel .timeline-content {
  border-left: 3px solid #e6a23c;
}

.timeline-content.transport-content {
  background: #f5f7fa;
  border-style: dashed;
}

.transport-route {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
}

.transport-route .from,
.transport-route .to {
  font-weight: 500;
  color: #303133;
}

.transport-route .arrow {
  color: #67c23a;
  font-weight: bold;
}

.transport-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #606266;
}

.item-address {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.schedule-item {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: move;
  transition: all 0.3s;
  position: relative;
}

.schedule-item:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.schedule-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.schedule-item.pending {
  border-style: dashed;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.item-tips {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
  padding: 6px;
  background: #fef0f0;
  border-radius: 4px;
}

.item-meta {
  font-size: 12px;
  color: #606266;
  display: flex;
  gap: 8px;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.hotel-item, .transport-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.hotel-item:hover, .transport-item:hover {
  background: #ecf5ff;
}

.item-icon {
  font-size: 24px;
}

.item-content {
  flex: 1;
}

.item-content strong {
  display: block;
  margin-bottom: 4px;
}

.item-content .address {
  color: #909399;
  font-size: 12px;
}

/* 右侧栏 (40%) */
.right-sidebar {
  background: white;
  border-left: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  position: relative;
  min-width: 450px;
  height: calc(100vh - 60px);  /* 固定高度，与页面同高 */
  overflow: hidden;  /* 防止溢出 */
}

.map-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
  flex-shrink: 0;  /* 防止header被压缩 */
}

.map-header h4 {
  margin: 0;
  font-size: 14px;
}

.map-container {
  flex: 1;
  position: relative;
  min-height: 0;  /* 重要：允许flex子元素收缩 */
  height: 100%;  /* 占满父容器 */
}

/* 确保高德地图canvas可以接收鼠标事件 */
.map-container > div {
  width: 100% !important;
  height: 100% !important;
}

.map-container canvas {
  pointer-events: auto !important;  /* 确保地图canvas可交互 */
}

/* 地图统计浮层 - 超紧凑样式 */
.map-stats-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.92);
  padding: 6px 10px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12);
  z-index: 999;
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.9);
  pointer-events: none;  /* 让鼠标事件穿透到地图 */
  max-width: 150px !important;  /* 严格限制宽度 */
  width: auto !important;
  min-width: 120px !important;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-item {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;  /* 防止换行 */
  line-height: 1.3;
}

.stats-item .label {
  font-size: 13px !important;  /* emoji大小 */
  flex-shrink: 0;
  width: 16px;
  text-align: center;
}

.stats-item .value {
  font-size: 11px !important;  /* 小字体 */
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 地图控制按钮 */
.map-controls {
  position: absolute;
  bottom: 24px;
  right: 24px;
  z-index: 999;
  pointer-events: auto;  /* 控制按钮需要可点击 */
}

/* 自定义标记样式 */
:deep(.amap-marker) {
  transition: transform 0.3s ease;
}

:deep(.amap-marker:hover) {
  transform: scale(1.1);
  z-index: 1000 !important;
}

/* 信息窗口样式 */
:deep(.info-window) {
  padding: 8px;
  min-width: 200px;
}

:deep(.info-window h4) {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #303133;
}

:deep(.info-window p) {
  margin: 4px 0;
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

/* 路线图例 */
.route-legend {
  position: absolute;
  bottom: 90px;
  right: 24px;
  background: rgba(255, 255, 255, 0.96);
  padding: 10px 12px;
  border-radius: 8px;
  box-shadow: 0 3px 12px rgba(0,0,0,0.2);
  z-index: 999;
  backdrop-filter: blur(12px);
  font-size: 11px;
  border: 1px solid rgba(255,255,255,0.8);
  max-width: 140px;
}

.route-legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.route-legend-item:last-child {
  margin-bottom: 0;
}

.route-legend-line {
  width: 30px;
  height: 3px;
  border-radius: 2px;
}

.route-legend-line.walking {
  background: currentColor;
}

.route-legend-line.driving {
  background: currentColor;
}

.route-legend-line.transit {
  background: currentColor;
  border-top: 2px dashed currentColor;
}

/* 详情面板 */
.detail-panel {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 45%;
  background: white;
  border-top: 2px solid #409eff;
  box-shadow: 0 -4px 16px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  overflow: hidden;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.detail-header {
  padding: 12px 16px;
  background: #409eff;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h4 {
  margin: 0;
  font-size: 14px;
}

.detail-body {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.detail-row .label {
  min-width: 60px;
  font-weight: 600;
  font-size: 12px;
  color: #606266;
}

.detail-row .value {
  flex: 1;
  font-size: 12px;
  color: #303133;
}

.detail-row .tips {
  flex: 1;
  padding: 8px;
  background: #fef0f0;
  border-left: 2px solid #f56c6c;
  font-size: 12px;
  border-radius: 4px;
}

/* 搜索对话框 */
.search-dialog-content {
  min-height: 400px;
}

.search-input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.search-categories {
  margin-bottom: 15px;
}

/* 搜索结果 */
.search-results {
  max-height: 450px;
  overflow-y: auto;
  margin-top: 10px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.result-item:hover {
  background: #f5f7fa;
  border-color: #409eff;
  transform: translateX(4px);
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.result-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
}

.result-content {
  flex: 1;
  min-width: 0;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.result-name {
  font-size: 15px;
  color: #303133;
  font-weight: 500;
}

.result-address {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #606266;
}

.result-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-extra {
  margin-top: 6px;
  padding: 4px 8px;
  background: #f0f9ff;
  border-radius: 4px;
  font-size: 12px;
}

.result-action {
  flex-shrink: 0;
}

.search-tips {
  margin-top: 20px;
}

.search-tips ul {
  margin: 10px 0;
  padding-left: 20px;
}

.search-tips li {
  margin: 6px 0;
  font-size: 13px;
  color: #606266;
}

/* 自动补全建议样式 */
.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.suggestion-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 6px;
}

.suggestion-content {
  flex: 1;
  min-width: 0;
}

.suggestion-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.suggestion-address {
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

