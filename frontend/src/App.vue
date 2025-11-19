<template>
  <div id="app">
    <div class="container-fluid">
      <!-- 頂部導航 -->
      <Header
          v-model:selectedMetric="selectedMetric"
          v-model:selectedChartType="selectedChartType"
          :viewType="currentView"
          :breadcrumbs="breadcrumbs"
          @navigate="handleNavigate"
      />

      <!-- 主要內容區 -->
      <div class="main-content">
        <!-- 地圖視圖 -->
        <div v-if="currentView === 'map'" class="map-wrapper">
          <MapSelector
              :selectedMetric="selectedMetric"
              :selectedYear="selectedYear"
              @country-selected="handleCountrySelected"
          />
        </div>

        <!-- 國家詳細視圖 -->
        <div v-else-if="currentView === 'country'" class="country-wrapper">
          <CountryDetail
              :countryInfo="selectedCountry"
              :selectedYear="selectedYear"
              :selectedChartType="selectedChartType"
              @back="backToMap"
          />
        </div>
      </div>

      <!-- 底部資訊條（僅在地圖視圖顯示） -->
      <div v-if="currentView === 'map' && hoverCountry" class="country-info">
        <span class="info-label">當前選擇：</span>
        <span class="country-name">{{ hoverCountry.name }}</span>
        <span class="separator">|</span>
        <span class="metric-value">{{ formatValue(hoverCountry) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Header from './components/Header.vue'
import MapSelector from './components/MapSelector.vue'
import CountryDetail from './components/CountryDetail.vue'

const selectedMetric = ref('tourist_count')
const selectedChartType = ref('monthly_tourists')
const selectedYear = ref(2019)
const currentView = ref('map') // 'map' | 'country'
const selectedCountry = ref(null)
const hoverCountry = ref(null)

const metricLabels = {
  tourist_count: '遊客流量',
  total_expenditure: '年度總消費額',
  avg_spending: '平均每人次消費',
  crowd_score: '擁擠程度'
}

// 麵包屑導航
const breadcrumbs = computed(() => {
  if (currentView.value === 'map') {
    return []
  } else if (currentView.value === 'country') {
    return [
      { label: '世界地圖', path: 'map', clickable: true },
      { label: selectedCountry.value?.name || '國家詳情', path: 'country', clickable: false }
    ]
  }
  return []
})

// 處理國家選擇（點擊地圖）
const handleCountrySelected = (country) => {
  console.log('選擇國家:', country)
  selectedCountry.value = country
  hoverCountry.value = country

  // 切換到國家詳細視圖
  currentView.value = 'country'
}

// 返回地圖
const backToMap = () => {
  currentView.value = 'map'
  selectedCountry.value = null
}

// 導航處理
const handleNavigate = (path) => {
  if (path === 'map') {
    backToMap()
  }
}

// 格式化數值
const formatValue = (country) => {
  if (!country) return ''

  if (country.metric === 'total_expenditure') {
    return `${metricLabels[country.metric]}: $${country.value.toLocaleString()}M`
  } else if (country.metric === 'avg_spending') {
    return `${metricLabels[country.metric]}: $${country.value.toFixed(2)} / 人次`
  } else if (country.metric === 'crowd_score') {
    return `${metricLabels[country.metric]}: ${country.value.toFixed(2)} / 100`
  } else {
    return `${metricLabels[country.metric]}: ${country.value.toLocaleString()} 人`
  }
}
</script>

<style>
/* 樣式保持不變 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', 'Arial', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #ffffff;
  min-height: 100vh;
  color: #000000;
}

.container-fluid {
  padding: 0;
  max-width: 100%;
}

.main-content {
  position: relative;
}

.map-wrapper {
  width: 100%;
  height: calc(100vh - 200px);
  padding: 2rem 3rem;
  background-color: #ffffff;
}

.country-wrapper {
  width: 100%;
  min-height: calc(100vh - 200px);
}

.country-info {
  position: fixed;
  bottom: 2rem;
  left: 3rem;
  padding: 1.5rem 2rem;
  background-color: #0369a1;
  color: #ffffff;
  border: 2px solid #0369a1;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(3, 105, 161, 0.3);
  z-index: 1000;
  border-radius: 4px;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-label {
  font-weight: 500;
  opacity: 0.9;
}

.country-name {
  font-weight: 700;
  font-size: 1.1rem;
}

.separator {
  opacity: 0.5;
}

.metric-value {
  font-weight: 500;
}

@media (max-width: 768px) {
  .map-wrapper {
    height: calc(100vh - 250px);
    padding: 1rem;
  }

  .country-info {
    left: 1rem;
    right: 1rem;
    bottom: 1rem;
    flex-wrap: wrap;
    font-size: 0.9rem;
  }
}
</style>