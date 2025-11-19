# 🌍 全球旅遊數據可視化系統

> 一個基於 plotly + Vue.js + Flask 的交互式全球旅遊數據分析平台
[![Plotly](https://img.shields.io/badge/plotly-6.5.0-blue.svg)]([https://www.docker.com/](https://plotly.com/python/))
[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 目錄

- [項目簡介](#項目簡介)
- [資料集來源](#項目簡介)
- [功能特性](#功能特性)
- [技術棧](#技術棧)
- [快速開始](#快速開始)
- [項目結構](#項目結構)
- [API 文檔](#api-文檔)
- [數據來源](#數據來源)
- [開發指南](#開發指南)
- [常見問題](#常見問題)
- [更新日誌](#更新日誌)
- [授權協議](#授權協議)

---

## 🎯 資料集來源

- map 各年國家總費用、各年國家旅遊入境人數 https://www.untourism.int/tourism-statistics/tourism-statistics-database
- JAPAN 國家個月入境人數 https://www.tourism.jp/wp/wp-content/uploads/2025/11/JTM_inbound_20251106eng.xlsx
- KOREA 個月入境人數 https://www.kaggle.com/datasets/bappekim/south-korea-visitors

全球旅遊數據可視化系統是一個用於分析和展示全球旅遊趨勢的交互式平台。系統整合了聯合國世界旅遊組織（UNWTO）的官方數據，提供直觀的地圖可視化、趨勢分析和國家詳細報告。

### 主要用途

- 📊 **旅遊行業分析**：幫助旅遊從業者了解市場趨勢
- 🎓 **學術研究**：為學者提供可靠的數據源和分析工具
- 🏛️ **政策制定**：協助政府機構進行旅遊政策規劃
- ✈️ **旅遊規劃**：幫助旅客選擇最佳旅遊時間和目的地

---

## 🎯 項目簡介

全球旅遊數據可視化系統是一個用於分析和展示全球旅遊趨勢的交互式平台。系統整合了聯合國世界旅遊組織（UNWTO）的官方數據，提供直觀的地圖可視化、趨勢分析和國家詳細報告。

### 主要用途

- 📊 **旅遊行業分析**：幫助旅遊從業者了解市場趨勢
- 🎓 **學術研究**：為學者提供可靠的數據源和分析工具
- 🏛️ **政策制定**：協助政府機構進行旅遊政策規劃
- ✈️ **旅遊規劃**：幫助旅客選擇最佳旅遊時間和目的地

---

## ✨ 功能特性

### 🗺️ 世界地圖可視化

- **多指標切換**
  - 遊客流量分析
  - 年度總消費額統計
  - 平均每人次消費計算
  - 旅遊擁擠程度評分

- **交互式地圖**
  - Plotly.js 驅動的高性能渲染
  - Hover 預覽國家數據
  - 點擊進入國家詳情頁面
  - 響應式設計，支持移動端

### 📈 國家詳細分析

#### 日本 🇯🇵
- **每月遊客數量趨勢圖**
  - 1996-1998 年歷史數據
  - 年度統計摘要（總計、平均、最高/最低月份）
  - 折線圖 + 區域填充可視化

#### 韓國 🇰🇷
- **每月遊客數量趨勢圖**
  - 2017-2020 年數據
  - 主要客源國分析
  - 同比增長率計算

#### 通用功能
- **消費結構分析**
  - 旅遊消費 vs 國際交通消費
  - 甜甜圈圓餅圖可視化
  - 詳細消費明細和百分比

### 🎨 UI/UX 設計

- **簡潔明快的界面**
  - 黑白配色 + 天藍色主題色 (#0ea5e9)
  - 卡片式佈局
  - 平滑動畫過渡

- **智能麵包屑導航**
  - 清晰的層級結構
  - 快速返回功能

- **計算型指標提示**
  - 懸浮顯示計算公式
  - 演算法說明
  - 實例展示

---

## 🛠️ 技術棧

### 前端
| 技術 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.x | 前端框架 |
| Plotly.js | latest | 數據可視化 |
| Axios | latest | HTTP 請求 |

### 後端
| 技術 | 版本 | 用途 |
|------|------|------|
| Python | 3.9 | 編程語言 |
| Flask | 2.x | Web 框架 |
| Flask-RESTful | latest | RESTful API |
| Pandas | latest | 數據處理 |
| NumPy | latest | 數值計算 |

### 部署工具
| 工具 | 用途 |
|------|------|
| Docker | 容器化 |
| Docker Compose | 多容器編排 |

---

## 🚀 快速開始

### 前置需求

- **Docker** (20.10+)
- **Docker Compose** (1.29+)

### 一鍵啟動（推薦）

```bash
# 1. 克隆項目
git clone https://github.com/box755/tourism-data-visualization.git
cd tourism-data-visualization

# 2. 構建並啟動服務
docker-compose up --build backend frontend

# 3. 訪問應用
前端: http://localhost:8080
後端: http://localhost:5000
```

### Docker 命令說明

```bash
# 啟動所有服務（後台運行）
docker-compose up -d backend frontend

# 查看運行狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend    # 後端日誌
docker-compose logs -f frontend   # 前端日誌

# 停止服務
docker-compose down

# 重新構建
docker-compose up --build backend frontend

# 進入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 驗證安裝

#### 測試後端 API

```bash
# 健康檢查
curl http://localhost:5000/healthy

# 獲取 2019 年世界地圖數據
curl http://localhost:5000/world-map-data?year=2019&metric=tourist_count

# 獲取日本月度數據
curl http://localhost:5000/country/JPN/monthly-visitors?year=1997
```

#### 測試前端

在瀏覽器訪問 `http://localhost:8080`，應該能看到世界地圖界面。

---

## 📁 項目結構

```
tourism-data-visualization/
├── backend/                           # 後端服務
│   ├── data/                          # 數據文件
│   │   ├── UN_Tourism_inbound_arrivals_10_2025.csv
│   │   ├── UN_Tourism_inbound_expenditure_10_2025.csv
│   │   ├── Japan_Monthly_Visitors.csv
│   │   └── Enter_korea_by_age(KOREA).csv
│   ├── src/
│   │   ├── api/                       # API 路由
│   │   │   ├── reports/               # 報表 API
│   │   │   │   ├── data.py            # 數據處理工具
│   │   │   │   ├── world_map_data.py  # 世界地圖遊客數據
│   │   │   │   ├── world_map_expenditure.py  # 總消費額
│   │   │   │   ├── world_map_avg_spending.py # 平均消費
│   │   │   │   ├── world_map_crowd_score.py  # 擁擠度評分
│   │   │   │   ├── japan_monthly_visitors.py # 日本月度數據
│   │   │   │   ├── korea_monthly_visitors.py # 韓國月度數據
│   │   │   │   ├── country_expenditure_breakdown.py # 消費結構
│   │   │   │   └── __init__.py
│   │   │   ├── healthcheck/
│   │   │   │   └── resources.py
│   │   │   └── __init__.py
│   │   ├── commons/                   # 共用工具
│   │   │   └── parser.py
│   │   ├── config.py                  # 配置文件
│   │   └── run.py                     # 啟動文件
│   ├── Dockerfile                     # 後端 Docker 配置
│   └── requirements.txt               # Python 依賴
│
├── frontend/                          # 前端應用
│   ├── public/
│   │   ├── index.html
│   │   └── exclamation-mark.svg       # 警告圖標
│   ├── src/
│   │   ├── apis/                      # API 接口封裝
│   │   │   ├── worldMap.js            # 世界地圖 API
│   │   │   └── country.js             # 國家詳情 API
│   │   ├── components/                # Vue 組件
│   │   │   ├── Header.vue             # 頂部導航欄
│   │   │   ├── MapSelector.vue        # 地圖選擇器
│   │   │   └── CountryDetail.vue      # 國家詳情頁
│   │   ├── utils/
│   │   │   └── http.js                # Axios 封裝
│   │   ├── App.vue                    # 主應用組件
│   │   └── main.js                    # 入口文件
│   ├── Dockerfile                     # 前端 Docker 配置
│   ├── package.json                   # npm 依賴
│   └── vue.config.js                  # Vue CLI 配置
│
├── docker-compose.yml                 # Docker Compose 配置
├── README.md                          # 項目文檔
└── .gitignore                         # Git 忽略文件
```

---

## 📡 API 文檔

### 基礎 URL

```
開發環境: http://localhost:5000
```

### 端點列表

#### 1. 健康檢查

```http
GET /healthy
```

**響應示例**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

#### 2. 世界地圖數據

**獲取遊客流量數據**
```http
GET /world-map-data?year=2019&metric=tourist_count
```

**參數**
- `year` (required): 年份 (1995-2023)
- `metric` (required): 指標類型 (`tourist_count`)

**響應示例**
```json
{
  "year": 2019,
  "metric": "tourist_count",
  "data": {
    "countries": ["CHN", "USA", "JPN", ...],
    "values": [162537900, 79300000, 31191856, ...]
  },
  "stats": {
    "total_countries": 195,
    "total_visitors": 1500000000
  }
}
```

**獲取總消費額**
```http
GET /world-map-expenditure?year=2019
```

**獲取平均消費**
```http
GET /world-map-avg-spending?year=2019
```

**獲取擁擠度評分**
```http
GET /world-map-crowd-score?year=2019
```

#### 3. 國家詳細數據

**日本每月遊客**
```http
GET /country/JPN/monthly-visitors?year=1997
```

**參數**
- `year` (optional): 年份，默認返回最新年份

**響應示例**
```json
{
  "country": "Japan",
  "country_code": "JPN",
  "year": 1997,
  "data": {
    "months": ["Jan", "Feb", "Mar", ...],
    "month_numbers": [1, 2, 3, ...],
    "values": [302148, 309318, 355228, ...],
    "changes": [9.4, 9.0, 14.3, ...]
  },
  "stats": {
    "year": 1997,
    "total_visitors": 4218208,
    "avg_visitors": 351517,
    "max_month": {
      "month": "Oct",
      "month_number": 10,
      "value": 419235
    },
    "min_month": {
      "month": "Dec",
      "month_number": 12,
      "value": 280991
    },
    "available_years": [1996, 1997, 1998]
  }
}
```

**韓國每月遊客**
```http
GET /country/KOR/monthly-visitors?year=2019
```

**消費結構分析**
```http
GET /country/{country_code}/expenditure-breakdown?year=2019
```

**支持的國家代碼**
- `FRA` - 法國
- `USA` - 美國
- `ESP` - 西班牙
- `CHN` - 中國
- 等（所有有數據的國家）

**響應示例**
```json
{
  "country": "France",
  "country_code": "FRA",
  "year": 2019,
  "data": {
    "categories": [
      {
        "name": "旅遊消費",
        "name_en": "Travel Expenditure",
        "value": 52000,
        "percentage": 80.0,
        "color": "#0ea5e9",
        "description": "住宿、餐飲、購物、當地交通等"
      },
      {
        "name": "國際交通",
        "name_en": "International Transport",
        "value": 13000,
        "percentage": 20.0,
        "color": "#f59e0b",
        "description": "國際機票、船票、跨國車票等"
      }
    ],
    "total": 65000,
    "currency": "million US dollars"
  },
  "metadata": {
    "calculation_method": "total_breakdown",
    "data_quality": "complete"
  }
}
```

### 錯誤處理

#### 404 Not Found
```json
{
  "error": "No data for year 2025",
  "year": 2025,
  "available_years": [1995, 1996, ..., 2023]
}
```

#### 500 Internal Server Error
```json
{
  "error": "無法讀取數據檔案: [error details]"
}
```

---

## 📊 數據來源

### 主要數據集

1. **UN Tourism Statistics Database**
   - **來源**: 聯合國世界旅遊組織 (UNWTO)
   - **覆蓋**: 195+ 國家和地區
   - **時間範圍**: 1995-2023
   - **更新頻率**: 每季度更新
   - **文件**:
     - `UN_Tourism_inbound_arrivals_10_2025.csv`
     - `UN_Tourism_inbound_expenditure_10_2025.csv`

2. **日本月度遊客數據**
   - **來源**: 日本觀光廳 (Japan Tourism Agency)
   - **時間範圍**: 1996-1998
   - **粒度**: 月度
   - **文件**: `Japan_Monthly_Visitors.csv`

3. **韓國入境遊客數據**
   - **來源**: 韓國文化體育觀光部
   - **時間範圍**: 2017-2020
   - **粒度**: 日度（按月聚合）
   - **文件**: `Enter_korea_by_age(KOREA).csv`

### 數據指標說明

#### 基礎指標（來自 UNWTO）

| 指標代碼 | 中文名稱 | 英文名稱 | 單位 |
|---------|---------|---------|------|
| `INBD_TRIP_AREA_TOTL_TOUR` | 總入境遊客 | Total Inbound Tourists | 千人 |
| `INBD_EXPD_BPAY_TOTL_VSTR` | 總消費額 | Total Expenditure | 百萬美元 |
| `INBD_EXPD_BPAY_TRVL_VSTR` | 旅遊消費 | Travel Expenditure | 百萬美元 |
| `INBD_EXPD_BPAY_PSTR_VSTR` | 國際交通消費 | Passenger Transport | 百萬美元 |

#### 計算指標

**平均每人次消費**
```
公式: 總消費額（百萬美元）÷ 遊客人次（千人）× 1000
單位: 美元/人次
演算法: Division (除法)
```

**旅遊擁擠程度評分**
```
公式: (該國遊客量 - 最小遊客量) ÷ (最大遊客量 - 最小遊客量) × 100
單位: 0-100 分
演算法: Min-Max Normalization (最小-最大標準化)
```

### 數據預估說明

#### 中國 2019 年數據
由於部分數據缺失，使用以下預估值：

| 指標 | 真實值 | 預估值 | 依據 |
|------|-------|-------|------|
| 旅遊消費 (TRVL) | $35,832M | - | 真實數據 ✅ |
| 國際交通 (PSTR) | - | $8,958M | 基於 20% 佔比估算 📊 |
| 總消費 (TOTL) | - | $44,790M | TRVL + PSTR 📊 |

**標記**: 預估數據在 CSV 中標記為 `flag: E, flag_label: Estimated`

---

## 💻 開發指南

### 本地開發（不使用 Docker）

#### 後端開發

```bash
# 1. 創建虛擬環境
cd backend
python -m venv venv

# 2. 激活虛擬環境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動開發服務器
python src/run.py

# 服務運行在 http://localhost:5000
```

#### 前端開發

```bash
# 1. 安裝依賴
cd frontend
npm install

# 2. 啟動開發服務器
npm run serve

# 服務運行在 http://localhost:8080
```

### 添加新國家月度數據

以添加「泰國」為例：

#### 1. 準備數據文件

創建 `backend/data/Thailand_Monthly_Visitors.csv`：

```csv
date,nation,visitor
2019-01,World,3500000
2019-02,World,3200000
...
```

#### 2. 創建 API 資源

創建 `backend/src/api/reports/thailand_monthly_visitors.py`：

```python
from flask import request
from flask_restful import Resource
from flask import current_app
import pandas as pd
from commons import parser

class ThailandMonthlyVisitorsResource(Resource):
    def get(self):
        path = current_app.config['BASE_DIR'] / 'data/Thailand_Monthly_Visitors.csv'
        df = pd.read_csv(path)
        
        # 解析和處理數據...
        # （參考 korea_monthly_visitors.py 的實現）
        
        return {
            'country': 'Thailand',
            'country_code': 'THA',
            'year': year,
            'data': data,
            'stats': stats
        }
```

#### 3. 註冊路由

在 `backend/src/api/reports/__init__.py` 中添加：

```python
from api.reports.thailand_monthly_visitors import ThailandMonthlyVisitorsResource

__all__ = [
    # ... 現有的
    'ThailandMonthlyVisitorsResource'
]
```

在 `backend/src/api/__init__.py` 中註冊：

```python
api.add_resource(
    reports.ThailandMonthlyVisitorsResource, 
    '/country/THA/monthly-visitors'
)
```

#### 4. 前端集成

在 `frontend/src/apis/country.js` 中添加：

```javascript
export function getThailandMonthlyVisitorsAPI(year) {
  return request({
    url: '/country/THA/monthly-visitors',
    params: { year }
  })
}
```

在 `frontend/src/components/CountryDetail.vue` 中添加支持：

```javascript
const loadMonthlyData = async () => {
  // ...
  else if (props.countryInfo.code === 'THA') {
    const data = await getThailandMonthlyVisitorsAPI(props.selectedYear)
    monthlyData.value = data
    // ...
  }
}
```

#### 5. 測試

```bash
# 重啟服務
docker-compose restart backend frontend

# 測試 API
curl http://localhost:5000/country/THA/monthly-visitors?year=2019

# 在前端點擊泰國查看效果
```

### 代碼規範

#### Python (PEP 8)
- 使用 4 空格縮排
- 每行最多 120 字符
- 函數和類之間空 2 行
- 使用 docstrings 註釋

#### JavaScript/Vue
- 使用 2 空格縮排
- 使用單引號
- 組件名使用 PascalCase
- 文件名使用 kebab-case

---

## ❓ 常見問題

### Docker 相關

**Q: 端口被佔用怎麼辦？**

```bash
# 查看佔用端口的進程
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# 修改 docker-compose.yml 中的端口映射
ports:
  - "5001:5000"  # 改為 5001
```

**Q: 如何重新構建鏡像？**

```bash
# 清除舊鏡像重新構建
docker-compose down
docker-compose build --no-cache backend frontend
docker-compose up backend frontend
```

**Q: 如何查看容器日誌？**

```bash
# 實時查看日誌
docker-compose logs -f backend

# 查看最近 100 行
docker-compose logs --tail=100 backend
```

### 數據相關

**Q: 為什麼某些國家沒有數據？**

A: UNWTO 數據集並非所有國家都有完整數據。可以通過 API 返回的 `available_years` 查看可用年份。

**Q: 如何更新數據？**

```bash
# 1. 下載最新 CSV 文件到 backend/data/
# 2. 重啟服務
docker-compose restart backend
```

**Q: 月度數據為什麼只有日本和韓國？**

A: 月度數據需要額外收集。其他國家的月度數據可以參考「添加新國家月度數據」章節自行添加。

### 前端相關

**Q: 地圖顏色如何修改？**

在 `frontend/src/components/MapSelector.vue` 中修改 `colorscale`：

```javascript
colorscale: [
  [0, '#ffffff'],    // 最小值顏色
  [1, '#0ea5e9']     // 最大值顏色
]
```

**Q: 如何添加新的圖表類型？**

1. 在 `Header.vue` 的 `chartTypeOptions` 中添加選項
2. 在 `CountryDetail.vue` 中添加對應的圖表組件
3. 創建對應的 API 端點

---

## 👨‍💻 作者

**box755**
- GitHub: [@box755](https://github.com/box755)

---

<p align="center">
  <img src="https://img.shields.io/badge/Made%20with-❤️-red.svg" alt="Made with love">
  <img src="https://img.shields.io/badge/Docker-ready-brightgreen.svg" alt="Docker ready">
  <img src="https://img.shields.io/badge/Vue.js-3.x-green.svg" alt="Vue 3">
  <img src="https://img.shields.io/badge/Flask-2.x-black.svg" alt="Flask 2">
</p>

<p align="center">
  Made with ❤️ by <strong>box755</strong>
</p>

<p align="center">
  © 2025 Tourism Data Visualization. All rights reserved.
</p>
