// 用來透過 axios 發送 http 請求

import axios from 'axios'

// axios.create 方法需傳入一個對象，其中有請求的部分配置，然後回傳一個方法
const httpInstance = axios.create({
    // 後端伺服器的基地址
    baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000',
    timeout: 10000
})

// 設定攔截器
// axios 請求攔截器 用來在 http 請求發送前先對請求處理
httpInstance.interceptors.request.use(config => {
    // 可以在這裡添加 token 或其他 header
    console.log(`🚀 Request: ${config.method?.toUpperCase()} ${config.url}`, config.params)
    return config
}, e => Promise.reject(e))

// axios 響應攔截器 用來在接收到 http 回應後對回應處理
httpInstance.interceptors.response.use(res => {
    console.log(`✅ Response: ${res.config.url}`, res.data)
    return res.data
}, e => {
    console.error('❌ Error:', e.response?.data || e.message)
    return Promise.reject(e)
})

// 導出
export default httpInstance