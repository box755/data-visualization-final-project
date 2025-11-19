<template>
  <div class="map-container">
    <div v-if="loading" class="loading-overlay">
      <p>載入地圖數據中...</p>
    </div>
    <div id="world-map" ref="mapContainer"></div>
    <div class="map-instruction">
      點擊地圖選擇國家
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Plotly from 'plotly.js-dist'
import {
  getWorldMapDataAPI,
  getWorldMapExpenditureAPI,
  getWorldMapAvgSpendingAPI,
  getWorldMapCrowdScoreAPI
} from '@/apis/worldMap.js'

const props = defineProps({
  selectedMetric: {
    type: String,
    default: 'tourist_count'
  },
  selectedYear: {
    type: Number,
    default: 2019
  }
})

const emit = defineEmits(['country-selected'])

const mapContainer = ref(null)
const mapData = ref(null)
const loading = ref(true)

const metricLabels = {
  tourist_count: '遊客流量',
  total_expenditure: '年度總消費額',
  avg_spending: '平均每人次消費',
  crowd_score: '旅遊擁擠程度'
}

const metricUnits = {
  tourist_count: '人',
  total_expenditure: '百萬美元',
  avg_spending: '美元/人次',
  crowd_score: '分'
}

// 從後端 API 獲取數據
const fetchMapData = async () => {
  try {
    loading.value = true

    let data
    if (props.selectedMetric === 'total_expenditure') {
      data = await getWorldMapExpenditureAPI(props.selectedYear)
    } else if (props.selectedMetric === 'avg_spending') {
      data = await getWorldMapAvgSpendingAPI(props.selectedYear)
    } else if (props.selectedMetric === 'crowd_score') {
      data = await getWorldMapCrowdScoreAPI(props.selectedYear)
    } else {
      data = await getWorldMapDataAPI(props.selectedYear, props.selectedMetric)
    }

    mapData.value = data
    initMap()
  } catch (error) {
    console.error('獲取地圖數據失敗:', error)
  } finally {
    loading.value = false
  }
}

const initMap = () => {
  if (!mapData.value || !mapContainer.value) return

  const { data } = mapData.value

  // 根據指標類型調整 hover 模板和顏色
  const unit = metricUnits[props.selectedMetric] || ''
  let hoverTemplate
  let colorscale

  if (props.selectedMetric === 'total_expenditure') {
    hoverTemplate = '<b>%{text}</b><br>' +
        metricLabels[props.selectedMetric] + ': $%{z:,.0f}M<br>' +
        '<extra></extra>'
    colorscale = [
      [0, '#f0f9ff'],
      [0.2, '#bae6fd'],
      [0.4, '#7dd3fc'],
      [0.6, '#38bdf8'],
      [0.8, '#0ea5e9'],
      [1, '#0369a1']
    ]
  } else if (props.selectedMetric === 'avg_spending') {
    hoverTemplate = '<b>%{text}</b><br>' +
        metricLabels[props.selectedMetric] + ': $%{z:,.2f}<br>' +
        '<extra></extra>'
    colorscale = [
      [0, '#f0f9ff'],
      [0.2, '#bae6fd'],
      [0.4, '#7dd3fc'],
      [0.6, '#38bdf8'],
      [0.8, '#0ea5e9'],
      [1, '#0369a1']
    ]
  } else if (props.selectedMetric === 'crowd_score') {
    hoverTemplate = '<b>%{text}</b><br>' +
        metricLabels[props.selectedMetric] + ': %{z:.2f} / 100<br>' +
        '<extra></extra>'
    colorscale = [
      [0, '#fef2f2'],
      [0.2, '#fecaca'],
      [0.4, '#fca5a5'],
      [0.6, '#f87171'],
      [0.8, '#ef4444'],
      [1, '#dc2626']
    ]
  } else {
    hoverTemplate = '<b>%{text}</b><br>' +
        metricLabels[props.selectedMetric] + ': %{z:,.0f} ' + unit + '<br>' +
        '<extra></extra>'
    colorscale = [
      [0, '#f0f9ff'],
      [0.2, '#bae6fd'],
      [0.4, '#7dd3fc'],
      [0.6, '#38bdf8'],
      [0.8, '#0ea5e9'],
      [1, '#0369a1']
    ]
  }

  const baseChoropleth = {
    type: 'choropleth',
    locationmode: 'ISO-3',
    locations: data.countries,
    z: data.values,
    text: data.country_names,
    hovertemplate: hoverTemplate,
    colorscale: colorscale,
    autocolorscale: false,
    reversescale: false,
    marker: {
      line: {
        color: '#000000',
        width: 1.5
      }
    },
    colorbar: {
      title: {
        text: metricLabels[props.selectedMetric],
        side: 'right',
        font: {
          size: 14,
          color: '#000000',
          family: 'Helvetica Neue, Arial, sans-serif'
        }
      },
      thickness: 20,
      len: 0.8,
      x: 1.02,
      tickfont: {
        color: '#000000',
        size: 12
      },
      outlinewidth: 2,
      outlinecolor: '#000000'
    },
    showscale: true
  }

  const plotData = [baseChoropleth]

  const layout = {
    geo: {
      projection: {
        type: 'natural earth'
      },
      showland: true,
      landcolor: '#f5f5f5',
      coastlinecolor: '#000000',
      coastlinewidth: 1,
      showcountries: true,
      countrycolor: '#000000',
      countrywidth: 1,
      showlakes: true,
      lakecolor: '#ffffff',
      showocean: true,
      oceancolor: '#ffffff',
      bgcolor: '#ffffff'
    },
    paper_bgcolor: '#ffffff',
    plot_bgcolor: '#ffffff',
    margin: { t: 20, b: 20, l: 20, r: 80 },
    height: window.innerHeight - 250,
    font: {
      family: 'Helvetica Neue, Arial, sans-serif',
      color: '#000000'
    }
  }

  const config = {
    responsive: true,
    displayModeBar: true,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    displaylogo: false,
    toImageButtonOptions: {
      format: 'png',
      filename: `tourism_map_${props.selectedYear}`,
      height: 1080,
      width: 1920,
      scale: 2
    }
  }

  Plotly.newPlot(mapContainer.value, plotData, layout, config)

  // 點擊事件 - 只發送事件，不改變地圖顏色
  mapContainer.value.on('plotly_click', (eventData) => {
    const point = eventData.points[0]
    const countryCode = point.location
    const countryIndex = data.countries.indexOf(countryCode)
    const countryName = data.country_names[countryIndex]
    const countryValue = point.z

    emit('country-selected', {
      code: countryCode,
      name: countryName,
      value: countryValue,
      metric: props.selectedMetric
    })
  })

  // Hover 事件 - 保留預覽效果
  mapContainer.value.on('plotly_hover', (eventData) => {
    const point = eventData.points[0]
    const countryCode = point.location
    previewCountry(countryCode, point.z, point.text)
  })

  // Unhover 事件 - 移除預覽
  mapContainer.value.on('plotly_unhover', () => {
    removePreview()
  })
}

// 預覽國家（hover 效果）
const previewCountry = (countryCode, value, name) => {
  if (!mapContainer.value) return

  const previewTrace = {
    type: 'choropleth',
    locationmode: 'ISO-3',
    locations: [countryCode],
    z: [value],
    text: [name],
    colorscale: [[0, 'rgba(252, 211, 77, 0.5)'], [1, 'rgba(252, 211, 77, 0.5)']],
    showscale: false,
    hoverinfo: 'skip',
    marker: {
      line: {
        color: '#FCD34D',
        width: 3
      }
    }
  }

  // 先移除舊的預覽層
  removePreview()

  // 添加新的預覽層
  Plotly.addTraces(mapContainer.value, previewTrace)
}

// 移除預覽效果
const removePreview = () => {
  if (!mapContainer.value || !mapContainer.value.data) return

  const traceCount = mapContainer.value.data.length

  // 只保留基礎地圖（trace 0）
  if (traceCount > 1) {
    const tracesToDelete = Array.from(
        { length: traceCount - 1 },
        (_, i) => i + 1
    )
    Plotly.deleteTraces(mapContainer.value, tracesToDelete)
  }
}

onMounted(() => {
  fetchMapData()

  window.addEventListener('resize', () => {
    if (mapData.value) {
      initMap()
    }
  })
})

watch(() => [props.selectedMetric, props.selectedYear], () => {
  fetchMapData()
}, { deep: true })
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
  border: 2px solid #000000;
  cursor: pointer;
}

#world-map {
  width: 100%;
  height: 100%;
}

.map-container:hover {
  box-shadow: 0 4px 12px rgba(3, 105, 161, 0.2);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  font-size: 1.2rem;
  font-weight: 500;
}

.map-instruction {
  position: absolute;
  top: 20px;
  left: 20px;
  background-color: #ffffff;
  color: #000000;
  padding: 0.75rem 1.5rem;
  border: 2px solid #000000;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.5px;
  z-index: 100;
  transition: all 0.3s ease;
}

.map-instruction:hover {
  background-color: #0ea5e9;
  color: #ffffff;
  border-color: #0ea5e9;
}
</style>