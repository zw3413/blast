<template>
  <div>
    <h1>WebSocket Client</h1>
    <input v-model="message" placeholder="Type a message" />
    <button @click="sendMessage">Send</button>
    <div v-for="msg in messages" :key="msg.id">
      {{ msg.text }}
    </div>
  </div>
</template>

<script>
let messageId = 0;

export default {
  data() {
    return {
      message: "",
      messages: [],
      socket: null,
    };
  },
  methods: {
    connectWebSocket() {
      this.socket = new WebSocket("ws://127.0.0.1:8000/ws");
      this.socket.onmessage = (event) => {
        this.messages.push({ id: messageId++, text: event.data });
      };
      this.socket.onopen = () => {
        console.log("WebSocket connection established.");
      };
      this.socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
      this.socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    },
    sendMessage() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(this.message);
        this.message = "";
      } else {
        console.error("WebSocket connection is not open.");
      }
    },
  },
  mounted() {
    //this.connectWebSocket();
  },
};
</script>

<style>
h1 {
  color: #333;
}
</style>
