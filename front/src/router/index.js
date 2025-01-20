import { createRouter, createWebHistory } from 'vue-router';
import WebSocketClient from '@/components/WebSocketClient.vue';
import Home from '@/components/home.vue'
import Blast from '@/components/blast.vue'
const routes = [
  {
    path: '/', // URL path for the WebSocket page
    name: 'Blast',
    component: Blast,
  },  
  // {
  //   path: '/blast', // URL path for the WebSocket page
  //   name: 'Blast',
  //   component: Blast,
  // },  
  // {
  //   path: '/websocket', // URL path for the WebSocket page
  //   name: 'WebSocket',
  //   component: WebSocketClient,
  // },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
