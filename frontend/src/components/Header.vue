<template>
  <div class="header">
    <div class="header-left">
      <h1 class="title">全球旅遊數據可視化</h1>
      <!-- 麵包屑導航 -->
      <div v-if="breadcrumbs.length > 0" class="breadcrumbs">
        <span
            v-for="(crumb, index) in breadcrumbs"
            :key="index"
            class="breadcrumb-item"
        >
          <span
              v-if="crumb.clickable"
              @click="$emit('navigate', crumb.path)"
              class="breadcrumb-link"
          >
            {{ crumb.label }}
          </span>
          <span v-else class="breadcrumb-current">{{ crumb.label }}</span>
          <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-separator">›</span>
        </span>
      </div>
    </div>

    <div class="header-right">
      <div class="metric-selector">
        <!-- 根據視圖類型顯示不同的 label -->
        <label for="metric-select">{{ selectorLabel }}：</label>
        <div class="select-wrapper">
          <!-- 自訂下拉選單 -->
          <div
              class="custom-select"
              :class="{ 'is-open': isSelectOpen }"
              @click="toggleSelect"
          >
            <div class="selected-option">
              <span>{{ selectedOptionInfo.label }}</span>
              <span class="dropdown-arrow">▼</span>
            </div>

            <div v-if="isSelectOpen" class="options-list">
              <div
                  v-for="option in currentOptions"
                  :key="option.value"
                  class="option-item"
                  :class="{ 'is-selected': currentValue === option.value }"
                  @click.stop="selectOption(option.value)"
              >
                <span>{{ option.label }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 計算方式提示圖示（只在地圖視圖且為計算型指標時顯示） -->
      <div
          v-if="viewType === 'map' && isCalculatedMetric"
          class="info-indicator"
          @mouseenter="showCalculationInfo = true"
          @mouseleave="showCalculationInfo = false"
      >
        <img src="/exclamation-mark.svg" class="info-icon" alt="計算方式說明" />

        <!-- 計算方式提示框 -->
        <div v-if="showCalculationInfo" class="calculation-tooltip">
          <div class="tooltip-header">
            <span class="tooltip-title">{{ calculationInfo.title }}</span>
          </div>
          <div class="tooltip-content">
            <div class="formula-section">
              <strong>計算公式：</strong>
              <div class="formula">{{ calculationInfo.formula }}</div>
            </div>
            <div class="description-section">
              <strong>說明：</strong>
              <p>{{ calculationInfo.description }}</p>
            </div>
            <div class="method-section" v-if="calculationInfo.method">
              <strong>演算法：</strong>
              <span class="method-badge">{{ calculationInfo.method }}</span>
            </div>
            <div class="example-section" v-if="calculationInfo.example">
              <strong>範例：</strong>
              <p class="example-text">{{ calculationInfo.example }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  // 地圖視圖的指標
  selectedMetric: {
    type: String,
    default: 'tourist_count'
  },
  // 國家詳細視圖的圖表類型
  selectedChartType: {
    type: String,
    default: 'monthly_tourists'
  },
  // 視圖類型：'map' | 'country'
  viewType: {
    type: String,
    default: 'map'
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:selectedMetric', 'update:selectedChartType', 'navigate'])

const isSelectOpen = ref(false)
const showCalculationInfo = ref(false)

// 地圖視圖 - 數據指標選項
const metricOptions = [
  { value: 'tourist_count', label: '遊客流量' },
  { value: 'total_expenditure', label: '年度總消費額' },
  { value: 'avg_spending', label: '平均每人次消費' },
  { value: 'crowd_score', label: '旅遊擁擠程度' }
]

// 國家詳細視圖 - 圖表類型選項
// 國家詳細視圖 - 圖表類型選項
const chartTypeOptions = [
  { value: 'monthly_tourists', label: '每月遊客數量' },
  { value: 'expenditure_breakdown', label: '消費結構分析' }  // 新增
  // { value: 'monthly_spending', label: '每月消費金額' },
  // { value: 'tourist_source', label: '遊客來源分布' },
  // { value: 'yearly_trend', label: '年度趨勢' }
]

// 計算型指標的詳細資訊
const calculationInfoMap = {
  avg_spending: {
    title: '平均每人次消費',
    formula: '平均消費 = 總消費額（百萬美元）÷ 遊客人次（千人）× 1000',
    description: '計算每位遊客平均在該國的消費金額，反映旅遊目的地的消費水平。數值越高表示該國旅遊消費越昂貴。',
    method: 'Division (除法)',
    example: '例如：法國總消費 $70,786M，遊客 90,000千人，則平均消費 = 70,786 ÷ 90 × 1000 = $786.51/人次'
  },
  crowd_score: {
    title: '旅遊擁擠程度',
    formula: '擁擠度 = (該國遊客量 - 最小遊客量) ÷ (最大遊客量 - 最小遊客量) × 100',
    description: '使用 Min-Max 標準化將各國遊客量歸一化到 0-100 分。100分代表最擁擠的國家，0分代表最少遊客的國家。',
    method: 'Rescaling (Min-Max Normalization)',
    example: '例如：中國遊客量最高得 100 分，小國遊客量少得 5-10 分，幫助比較不同規模國家的擁擠程度。'
  }
}

// 根據視圖類型返回不同的選項
const currentOptions = computed(() => {
  return props.viewType === 'map' ? metricOptions : chartTypeOptions
})

// 根據視圖類型返回當前值
const currentValue = computed(() => {
  return props.viewType === 'map' ? props.selectedMetric : props.selectedChartType
})

// 根據視圖類型返回選擇器標籤
const selectorLabel = computed(() => {
  return props.viewType === 'map' ? '數據指標' : '圖表類型'
})

// 當前選中的選項資訊
const selectedOptionInfo = computed(() => {
  const options = currentOptions.value
  const value = currentValue.value
  return options.find(opt => opt.value === value) || options[0]
})

// 判斷當前指標是否為計算型（僅在地圖視圖）
const isCalculatedMetric = computed(() => {
  if (props.viewType !== 'map') return false
  return ['avg_spending', 'crowd_score'].includes(props.selectedMetric)
})

// 獲取當前指標的計算資訊
const calculationInfo = computed(() => {
  return calculationInfoMap[props.selectedMetric] || {}
})

// 切換下拉選單
const toggleSelect = () => {
  isSelectOpen.value = !isSelectOpen.value
}

// 選擇選項
const selectOption = (value) => {
  if (props.viewType === 'map') {
    emit('update:selectedMetric', value)
  } else {
    emit('update:selectedChartType', value)
  }
  isSelectOpen.value = false
}

// 點擊外部關閉下拉選單
const handleClickOutside = (event) => {
  const selectWrapper = document.querySelector('.select-wrapper')
  const infoIndicator = document.querySelector('.info-indicator')

  if (selectWrapper && !selectWrapper.contains(event.target) &&
      (!infoIndicator || !infoIndicator.contains(event.target))) {
    isSelectOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* 樣式保持不變 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 3rem;
  border-bottom: 2px solid #000000;
  background-color: #ffffff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #000000;
  margin: 0;
}

/* 麵包屑導航 */
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #6B7280;
}

.breadcrumb-link {
  color: #0ea5e9;
  cursor: pointer;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #0369a1;
  text-decoration: underline;
}

.breadcrumb-current {
  color: #000000;
  font-weight: 600;
}

.breadcrumb-separator {
  color: #D1D5DB;
  margin: 0 0.25rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.metric-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.metric-selector label {
  font-size: 1rem;
  font-weight: 500;
  color: #000000;
}

.select-wrapper {
  position: relative;
}

/* 自訂下拉選單 */
.custom-select {
  position: relative;
  min-width: 240px;
  cursor: pointer;
  user-select: none;
}

.selected-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid #000000;
  background-color: #ffffff;
  color: #000000;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.custom-select:hover .selected-option {
  background-color: #0ea5e9;
  color: #ffffff;
  border-color: #0ea5e9;
}

.custom-select.is-open .selected-option {
  background-color: #0369a1;
  color: #ffffff;
  border-color: #0369a1;
}

.dropdown-arrow {
  margin-left: auto;
  font-size: 0.7rem;
  transition: transform 0.3s ease;
}

.custom-select.is-open .dropdown-arrow {
  transform: rotate(180deg);
}

/* 選項列表 */
.options-list {
  position: absolute;
  top: calc(100% + 5px);
  left: 0;
  right: 0;
  background-color: #ffffff;
  border: 2px solid #000000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #e5e7eb;
}

.option-item:last-child {
  border-bottom: none;
}

.option-item:hover {
  background-color: #0ea5e9;
  color: #ffffff;
}

.option-item.is-selected {
  background-color: #f0f9ff;
  font-weight: 600;
}

/* 計算方式提示圖示 */
.info-indicator {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background-color: #FEF3C7;
  border: 2px solid #F59E0B;
  border-radius: 50%;
  cursor: help;
  transition: all 0.3s ease;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 8px rgba(245, 158, 11, 0);
  }
}

.info-indicator:hover {
  background-color: #FCD34D;
  border-color: #D97706;
  transform: scale(1.1);
  animation: none;
}

.info-icon {
  width: 24px;
  height: 24px;
}

/* 計算方式提示框 */
.calculation-tooltip {
  position: absolute;
  top: calc(100% + 15px);
  right: 0;
  width: 450px;
  background-color: #ffffff;
  border: 2px solid #F59E0B;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideDown 0.3s ease-out;
}

.calculation-tooltip::before {
  content: '';
  position: absolute;
  top: -10px;
  right: 20px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 10px solid #F59E0B;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-bottom: 2px solid #F59E0B;
  border-radius: 5px 5px 0 0;
}

.tooltip-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #92400E;
}

.tooltip-content {
  padding: 1.2rem;
}

.formula-section,
.description-section,
.method-section,
.example-section {
  margin-bottom: 1.25rem;
}

.formula-section:last-child,
.description-section:last-child,
.method-section:last-child,
.example-section:last-child {
  margin-bottom: 0;
}

.tooltip-content strong {
  display: block;
  color: #000000;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.95rem;
}

.formula {
  background-color: #F3F4F6;
  padding: 0.875rem;
  border-left: 4px solid #0ea5e9;
  font-family: 'Courier New', monospace;
  font-size: 0.6rem;
  color: #1F2937;
  line-height: 1.6;
  border-radius: 4px;
}

.description-section p {
  color: #4B5563;
  line-height: 1.7;
  font-size: 0.8rem;
  margin: 0;
}

.method-badge {
  display: inline-block;
  background-color: #DBEAFE;
  color: #1E40AF;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #3B82F6;
}

.example-text {
  background-color: #FEF3C7;
  padding: 0.8rem;
  border-left: 4px solid #F59E0B;
  color: #92400E;
  font-size: 0.8rem;
  line-height: 1.6;
  margin: 0;
  border-radius: 4px;
  font-style: italic;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .header-left {
    width: 100%;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .title {
    font-size: 1.5rem;
  }

  .metric-selector {
    flex-direction: column;
    align-items: stretch;
  }

  .custom-select {
    width: 100%;
  }

  .info-indicator {
    align-self: center;
  }

  .calculation-tooltip {
    width: calc(100vw - 3rem);
    right: auto;
    left: 50%;
    transform: translateX(-50%);
  }

  .calculation-tooltip::before {
    left: 50%;
    transform: translateX(-50%);
  }
}
</style>