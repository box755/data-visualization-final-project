<template>
  <div class="country-detail">
    <div v-if="loading" class="loading-overlay">
      <p>載入國家數據中...</p>
    </div>

    <div v-else class="detail-content">
      <!-- 國家標題區 -->
      <div class="country-header">
        <div class="country-title-section">
          <h2 class="country-name">{{ countryInfo.name }}</h2>
          <span class="country-code">{{ countryInfo.code }}</span>
        </div>
        <button class="back-button" @click="handleBackToMap">
          <span class="back-arrow">←</span>
          <span>返回地圖</span>
        </button>
      </div>

      <!-- 數據卡片 -->
      <div class="stats-grid">
        <div class="stat-card" v-if="countryData.tourist_count">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <div class="stat-label">遊客流量</div>
            <div class="stat-value">{{ formatNumber(countryData.tourist_count) }}</div>
            <div class="stat-unit">人</div>
          </div>
        </div>

        <div class="stat-card" v-if="countryData.total_expenditure">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <div class="stat-label">年度總消費額</div>
            <div class="stat-value">${{ formatNumber(countryData.total_expenditure) }}M</div>
            <div class="stat-unit">百萬美元</div>
          </div>
        </div>

        <div class="stat-card" v-if="countryData.avg_spending">
          <div class="stat-icon">💳</div>
          <div class="stat-content">
            <div class="stat-label">平均每人次消費</div>
            <div class="stat-value">${{ countryData.avg_spending.toFixed(2) }}</div>
            <div class="stat-unit">美元/人次</div>
          </div>
        </div>

        <div class="stat-card" v-if="countryData.crowd_score !== undefined">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-label">擁擠程度</div>
            <div class="stat-value">{{ countryData.crowd_score.toFixed(1) }}</div>
            <div class="stat-unit">/ 100</div>
          </div>
        </div>
      </div>

      <!-- 圖表區域 -->
      <div class="charts-section">
        <h3 class="chart-title">📈 {{ chartTitle }}</h3>

        <!-- 每月遊客數量圖表 -->
        <div v-if="selectedChartType === 'monthly_tourists'" class="chart-container">
          <div v-if="monthlyData" class="chart-content">
            <div id="monthly-chart" ref="monthlyChartContainer"></div>

            <!-- 月度統計摘要 -->
            <div class="monthly-stats">
              <div class="stat-item">
                <span class="stat-label">年度總計：</span>
                <span class="stat-value">{{ formatNumber(monthlyStats.total) }} 人</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">月均人數：</span>
                <span class="stat-value">{{ formatNumber(monthlyStats.average) }} 人</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">最高月份：</span>
                <span class="stat-value">{{ monthlyStats.maxMonth }} ({{ formatNumber(monthlyStats.maxValue) }})</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">最低月份：</span>
                <span class="stat-value">{{ monthlyStats.minMonth }} ({{ formatNumber(monthlyStats.minValue) }})</span>
              </div>
            </div>
          </div>
          <div v-else class="chart-placeholder">
            <p>📊 該國家暫無每月遊客數量數據</p>
            <p class="placeholder-hint">目前只支持日本的月度數據</p>
          </div>
        </div>

        <!-- 消費結構分析圓餅圖 -->
        <div v-else-if="selectedChartType === 'expenditure_breakdown'" class="chart-container">
          <div v-if="expenditureData" class="chart-content">
            <div id="expenditure-chart" ref="expenditureChartContainer"></div>

            <!-- 消費明細 -->
            <div class="expenditure-details">
              <h4 class="details-title">消費明細</h4>
              <div
                  v-for="category in expenditureData.data.categories"
                  :key="category.name"
                  class="detail-item"
              >
                <div class="detail-header">
                  <span
                      class="color-indicator"
                      :style="{ backgroundColor: category.color }"
                  ></span>
                  <span class="category-name">{{ category.name }}</span>
                  <span class="category-percentage">{{ category.percentage.toFixed(1) }}%</span>
                </div>
                <div class="detail-content">
                  <div class="detail-value">${{ formatNumber(category.value) }}M</div>
                  <div class="detail-description">{{ category.description }}</div>
                </div>
              </div>

              <div class="detail-total">
                <span>總計：</span>
                <span class="total-value">${{ formatNumber(expenditureData.data.total) }}M</span>
              </div>
            </div>
          </div>
          <div v-else class="chart-placeholder">
            <p>📊 該國家暫無消費結構數據</p>
            <p class="placeholder-hint">需要同時有旅遊消費和交通消費數據</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import {
  getWorldMapDataAPI,
  getWorldMapExpenditureAPI,
  getWorldMapAvgSpendingAPI,
  getWorldMapCrowdScoreAPI
} from '@/apis/worldMap.js'
import {
  getJapanMonthlyVisitorsAPI,
  getCountryExpenditureBreakdownAPI,
  getKoreaMonthlyVisitorsAPI
} from '@/apis/country.js'

const props = defineProps({
  countryInfo: {
    type: Object,
    required: true
  },
  selectedYear: {
    type: Number,
    default: 2019
  },
  selectedChartType: {
    type: String,
    default: 'monthly_tourists'
  }
})

const emit = defineEmits(['back'])

const loading = ref(true)
const countryData = ref({})
const monthlyData = ref(null)
const expenditureData = ref(null)
const monthlyChartContainer = ref(null)
const expenditureChartContainer = ref(null)

// 圖表標題
const chartTitle = computed(() => {
  const titles = {
    monthly_tourists: `${props.selectedYear} 年每月遊客數量趨勢`,
    expenditure_breakdown: `${props.selectedYear} 年旅遊消費結構分析`
  }
  return titles[props.selectedChartType] || '數據圖表'
})

// 月度統計
const monthlyStats = computed(() => {
  if (!monthlyData.value || !monthlyData.value.stats) {
    return {
      total: 0,
      average: 0,
      maxMonth: '-',
      maxValue: 0,
      minMonth: '-',
      minValue: 0
    }
  }

  const stats = monthlyData.value.stats
  return {
    total: stats.total_visitors,
    average: stats.avg_visitors,
    maxMonth: stats.max_month.month,
    maxValue: stats.max_month.value,
    minMonth: stats.min_month.month,
    minValue: stats.min_month.value
  }
})

// 格式化數字
const formatNumber = (num) => {
  return num.toLocaleString()
}

// 返回地圖
const handleBackToMap = () => {
  emit('back')
}

// 載入國家所有數據
const loadCountryData = async () => {
  try {
    loading.value = true

    const promises = [
      getWorldMapDataAPI(props.selectedYear, 'tourist_count'),
      getWorldMapExpenditureAPI(props.selectedYear),
      getWorldMapAvgSpendingAPI(props.selectedYear),
      getWorldMapCrowdScoreAPI(props.selectedYear)
    ]

    const [touristData, expenditureData, avgSpendingData, crowdScoreData] = await Promise.all(promises)

    const countryCode = props.countryInfo.code

    // 遊客流量
    const touristIndex = touristData.data.countries.indexOf(countryCode)
    if (touristIndex !== -1) {
      countryData.value.tourist_count = touristData.data.values[touristIndex]
    }

    // 總消費額
    const expenditureIndex = expenditureData.data.countries.indexOf(countryCode)
    if (expenditureIndex !== -1) {
      countryData.value.total_expenditure = expenditureData.data.values[expenditureIndex]
    }

    // 平均消費
    const avgSpendingIndex = avgSpendingData.data.countries.indexOf(countryCode)
    if (avgSpendingIndex !== -1) {
      countryData.value.avg_spending = avgSpendingData.data.values[avgSpendingIndex]
    }

    // 擁擠度
    const crowdScoreIndex = crowdScoreData.data.countries.indexOf(countryCode)
    if (crowdScoreIndex !== -1) {
      countryData.value.crowd_score = crowdScoreData.data.values[crowdScoreIndex]
    }

    // 根據選擇的圖表類型載入對應數據
    await loadChartData()

    console.log('國家數據:', countryData.value)
  } catch (error) {
    console.error('載入國家數據失敗:', error)
  } finally {
    loading.value = false
  }
}

// 載入圖表數據
const loadChartData = async () => {
  if (props.selectedChartType === 'monthly_tourists') {
    await loadMonthlyData()
  } else if (props.selectedChartType === 'expenditure_breakdown') {
    await loadExpenditureBreakdown()
  }
}

// 載入每月遊客數據
const loadMonthlyData = async () => {
  try {
    // 支持日本和韓國
    if (props.countryInfo.code === 'JPN') {
      const data = await getJapanMonthlyVisitorsAPI(props.selectedYear)
      monthlyData.value = data
      console.log('日本月度數據:', data)

      setTimeout(() => {
        initMonthlyChart()
      }, 100)
    } else if (props.countryInfo.code === 'KOR') {
      const data = await getKoreaMonthlyVisitorsAPI(props.selectedYear)
      monthlyData.value = data
      console.log('韓國月度數據:', data)

      setTimeout(() => {
        initMonthlyChart()
      }, 100)
    } else {
      monthlyData.value = null
    }
  } catch (error) {
    console.error('載入月度數據失敗:', error)
    monthlyData.value = null
  }
}

// 載入消費結構數據
const loadExpenditureBreakdown = async () => {
  try {
    const data = await getCountryExpenditureBreakdownAPI(
        props.countryInfo.code,
        props.selectedYear
    )
    expenditureData.value = data
    console.log('消費結構數據:', data)

    setTimeout(() => {
      initExpenditureChart()
    }, 100)
  } catch (error) {
    console.error('載入消費結構失敗:', error)
    expenditureData.value = null
  }
}

// 初始化月度圖表
const initMonthlyChart = () => {
  if (!monthlyData.value || !monthlyChartContainer.value) return

  const { data } = monthlyData.value

  const trace = {
    x: data.months,
    y: data.values,
    type: 'scatter',
    mode: 'lines+markers',
    name: '遊客人數',
    line: {
      color: '#0ea5e9',
      width: 3
    },
    marker: {
      color: '#0ea5e9',
      size: 8,
      line: {
        color: '#ffffff',
        width: 2
      }
    },
    fill: 'tozeroy',
    fillcolor: 'rgba(14, 165, 233, 0.1)',
    hovertemplate: '<b>%{x}</b><br>' +
        '遊客數：%{y:,.0f} 人<br>' +
        '<extra></extra>'
  }

  const layout = {
    title: {
      text: '',
      font: { size: 16, color: '#000000' }
    },
    xaxis: {
      title: '月份',
      showgrid: true,
      gridcolor: '#E5E7EB',
      linecolor: '#000000',
      linewidth: 2
    },
    yaxis: {
      title: '遊客人數',
      showgrid: true,
      gridcolor: '#E5E7EB',
      linecolor: '#000000',
      linewidth: 2,
      tickformat: ',.0f'
    },
    plot_bgcolor: '#ffffff',
    paper_bgcolor: '#ffffff',
    margin: { t: 40, r: 40, b: 60, l: 80 },
    height: 400,
    font: {
      family: 'Helvetica Neue, Arial, sans-serif',
      color: '#000000'
    }
  }

  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false
  }

  Plotly.newPlot(monthlyChartContainer.value, [trace], layout, config)
}

// 初始化消費結構圓餅圖
const initExpenditureChart = () => {
  if (!expenditureData.value || !expenditureChartContainer.value) return

  const { categories } = expenditureData.value.data

  const trace = {
    type: 'pie',
    labels: categories.map(c => c.name),
    values: categories.map(c => c.value),
    marker: {
      colors: categories.map(c => c.color),
      line: {
        color: '#ffffff',
        width: 2
      }
    },
    textinfo: 'label+percent',
    textposition: 'inside',
    textfont: {
      size: 14,
      color: '#ffffff',
      family: 'Helvetica Neue, Arial, sans-serif'
    },
    hovertemplate: '<b>%{label}</b><br>' +
        '金額：$%{value:,.0f}M<br>' +
        '佔比：%{percent}<br>' +
        '<extra></extra>',
    hole: 0.4  // 甜甜圈圖
  }

  const layout = {
    title: {
      text: '',
      font: { size: 16 }
    },
    showlegend: true,
    legend: {
      orientation: 'v',
      x: 1.1,
      y: 0.5,
      font: {
        size: 13,
        family: 'Helvetica Neue, Arial, sans-serif'
      }
    },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
    margin: { t: 40, r: 150, b: 40, l: 40 },
    height: 400,
    font: {
      family: 'Helvetica Neue, Arial, sans-serif',
      size: 14,
      color: '#000000'
    }
  }

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d']
  }

  Plotly.newPlot(expenditureChartContainer.value, [trace], layout, config)
}

// 監聽年份變化
watch(() => props.selectedYear, () => {
  loadChartData()
})

// 監聽圖表類型變化
watch(() => props.selectedChartType, () => {
  loadChartData()
})

onMounted(() => {
  loadCountryData()
})
</script>

<style scoped>
.country-detail {
  width: 100%;
  min-height: calc(100vh - 200px);
  padding: 2rem 3rem;
  background-color: #ffffff;
}

.loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  font-size: 1.2rem;
  font-weight: 500;
  color: #6B7280;
}

.detail-content {
  max-width: 1400px;
  margin: 0 auto;
}

/* 國家標題區 */
.country-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #E5E7EB;
}

.country-title-section {
  display: flex;
  align-items: baseline;
  gap: 1rem;
}

.country-name {
  font-size: 2.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.country-code {
  font-size: 1.2rem;
  color: #6B7280;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  background-color: #F3F4F6;
  border-radius: 4px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #ffffff;
  border: 2px solid #000000;
  color: #000000;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: #0ea5e9;
  color: #ffffff;
  border-color: #0ea5e9;
}

.back-arrow {
  font-size: 1.2rem;
}

/* 數據卡片網格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background-color: #ffffff;
  border: 2px solid #000000;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #0ea5e9;
}

.stat-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #6B7280;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 0.25rem;
}

.stat-unit {
  font-size: 0.85rem;
  color: #9CA3AF;
}

/* 圖表區域 */
.charts-section {
  margin-top: 3rem;
}

.chart-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 1.5rem;
}

.chart-container {
  background-color: #ffffff;
  border: 2px solid #000000;
  border-radius: 8px;
  padding: 2rem;
  min-height: 400px;
}

.chart-content {
  width: 100%;
}

#monthly-chart,
#expenditure-chart {
  width: 100%;
  min-height: 400px;
}

/* 月度統計摘要 */
.monthly-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #E5E7EB;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-item .stat-label {
  font-size: 0.9rem;
  color: #6B7280;
  font-weight: 500;
}

.stat-item .stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0ea5e9;
}

/* 消費結構詳情 */
.expenditure-details {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #F9FAFB;
  border-radius: 8px;
}

.details-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 1rem;
}

.detail-item {
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #ffffff;
  border: 1px solid #E5E7EB;
  border-radius: 6px;
}

.detail-item:last-of-type {
  margin-bottom: 0;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.color-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
}

.category-name {
  font-weight: 600;
  color: #000000;
  flex: 1;
}

.category-percentage {
  font-weight: 700;
  color: #0ea5e9;
  font-size: 1.1rem;
}

.detail-content {
  margin-left: 28px;
}

.detail-value {
  font-size: 1.3rem;
  font-weight: 700;
  color: #000000;
  margin-bottom: 0.25rem;
}

.detail-description {
  font-size: 0.9rem;
  color: #6B7280;
}

.detail-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #E5E7EB;
  font-size: 1.1rem;
  font-weight: 600;
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0ea5e9;
}

/* 佔位符 */
.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  background-color: #F9FAFB;
  border: 2px dashed #D1D5DB;
  border-radius: 8px;
  text-align: center;
  color: #6B7280;
}

.chart-placeholder p {
  font-size: 1.2rem;
  margin: 0.5rem 0;
}

.placeholder-hint {
  font-size: 0.9rem !important;
  color: #9CA3AF;
}

@media (max-width: 768px) {
  .country-detail {
    padding: 1.5rem;
  }

  .country-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .country-name {
    font-size: 2rem;
  }

  .back-button {
    width: 100%;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .monthly-stats {
    grid-template-columns: 1fr;
  }
}
</style>