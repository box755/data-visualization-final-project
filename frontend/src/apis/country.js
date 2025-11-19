import request from '@/utils/http.js'

/**
 * 獲取日本每月遊客數量
 */
export function getJapanMonthlyVisitorsAPI(year) {
    return request({
        url: '/country/JPN/monthly-visitors',
        params: { year }
    })
}

/**
 * 獲取韓國每月遊客數量
 */
export function getKoreaMonthlyVisitorsAPI(year) {
    return request({
        url: '/country/KOR/monthly-visitors',
        params: { year }
    })
}

/**
 * 獲取國家消費結構分析
 */
export function getCountryExpenditureBreakdownAPI(countryCode, year) {
    return request({
        url: `/country/${countryCode}/expenditure-breakdown`,
        params: { year }
    })
}