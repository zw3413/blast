import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import { dynamicBase } from 'vite-plugin-dynamic-base'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    //vueDevTools(),
    // dynamicBase({
    //   // dynamic public path var string, default window.__dynamic_base__
    //   publicPath: '',
    //   // dynamic load resources on index.html, default false. maybe change default true
    //   transformIndexHtml: false
    // })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  base: '/',
})
