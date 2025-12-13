import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 开发服务器配置
  server: {
    port: 5173,
    // 代理配置 - 解决跨域问题
    proxy: {
      '/auth': {
        target: 'http://localhost:8000',  // 后端Flask地址
        changeOrigin: true,
        // 不需要rewrite，因为后端路由本身就是 /auth/xxx
      },
      '/market': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/transaction': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
