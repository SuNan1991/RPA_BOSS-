import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './styles/theme.css'
import { setupErrorHandling } from './utils/errorHandler'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 设置全局错误处理
setupErrorHandling()

// Vue组件错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err, info)
  // 错误已在setupErrorHandling中通过window.onerror处理
}

app.mount('#app')
