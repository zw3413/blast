import './assets/main.css'
import './assets/tailwind.css';
import router from './router';

import { createApp } from 'vue'
import App from './App.vue'
import layui from '@layui/layui-vue'
import '@layui/layui-vue/lib/index.css'

const app = createApp(App)
app.config.devtools = false;
app.use(router).use(layui).mount('#app')