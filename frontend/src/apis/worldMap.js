import request from '@/utils/http.js'

/**
 * 獲取世界地圖遊客流量數據
 */
export function getWorldMapDataAPI(year, metric) {
    return request({
        url: '/world-map-data',
        params: { year, metric }
    })
}

/**
 * 獲取世界地圖遊客消費數據
 */
export function getWorldMapExpenditureAPI(year) {
    return request({
        url: '/world-map-expenditure',
        params: { year }
    })
}

/**
 * 獲取世界地圖平均每人次消費數據
 */
export function getWorldMapAvgSpendingAPI(year) {
    return request({
        url: '/world-map-avg-spending',
        params: { year }
    })
}

/**
 * 獲取世界地圖旅遊擁擠度數據
 */
export function getWorldMapCrowdScoreAPI(year) {
    return request({
        url: '/world-map-crowd-score',
        params: { year }
    })
}