<script setup>
import { onMounted, createApp } from 'vue';


const app = createApp({
  onMounted : () => {
    const video1 = document.getElementById('video1');
    const video2 = document.getElementById('video2');

    // Synchronize play/pause
    video1.addEventListener('play', () => {
      if (video2.paused) video2.play();
    });
    video1.addEventListener('pause', () => {
      video2.pause();
    });

    video2.addEventListener('play', () => {
      if (video1.paused) video1.play();
    });
    video2.addEventListener('pause', () => {
      video1.pause();
    });

    // Synchronize seeking
    video1.addEventListener('seeked', () => {
      video2.currentTime = video1.currentTime;
    });
    video2.addEventListener('seeked', () => {
      video1.currentTime = video2.currentTime;
    });

    // Synchronize volume (optional)
    video1.addEventListener('volumechange', () => {
      video2.volume = video1.volume;
    });
    video2.addEventListener('volumechange', () => {
      video1.volume = video2.volume;
    });

    // Load video sources (you'll need to set the src attribute)
    video1.src = "video1.mp4"; // Replace with your video URLs
    video2.src = "video2.mp4";
  }
})

</script>

<template>
  <header>

  </header>

  <main>
    <div class="video-container">11
      <video id="video1"></video>
      <video id="video2"></video>
    </div>
    <div class="controls">
      <button id="play-pause">Play/Pause</button>
    </div>
  </main>
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  .video-container {
    display: flex;
    /* Use flexbox for easy layout */
  }

  .video-container video {
    width: 50%;
    /* Each video takes up half the container width */
    height: auto;
    /* Maintain aspect ratio */
  }
}
</style>
