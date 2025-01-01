<template>
    <div class="flex flex-row w-full min-h-screen max-h-screen overflow-hidden">
        <div class="">
            <div class="flex flex-row">
                <input type="text" v-model="analysis_name">
                <button type="button" @click="createHandler" class="ml-auto text-white  ">create</button>
            </div>
            <ul>
                <li v-for="analysis in analysis_list" :key="analysis.id">
                    <a @click="getVideos(analysis.id)"> {{ analysis.name }}</a>
                </li>
            </ul>
        </div>

        <div class="w-full min-h-screen">
            <div class=" h-3/4 bg-black">
                <div v-show="show == 'video'" class=" w-full h-full flex flex-row">
                    <div class="flex flex-col space-y-2 ">
                        <input type="checkbox" class="flex mt-10" v-model="canvasCheckbox" />Draw
                        <button class="flex" @click="drawType = 'point'">point</button>
                        <button class="flex" @click="drawType = 'line'">line</button>
                        <button class="flex" @click="drawType = 'rect'">rect</button>
                        <button class="flex" @click="drawType = 'circle'">circle</button>
                        <button class="flex">clear</button>
                    </div>
                    <div class=" w-full h-full p-6 relative">
                        <div class="absolute inset-x-0 bottom-5 items-center justify-center">
                        <video id="my-video" class=" video-js vjs-fluid vjs-default-skin w-full h-full" controls
                            preload="auto" :data-setup="videoSetupOptions" @loadedmetadata="resizeCanvas">
                            <source :src="playingVideo" type="video/mp4" />
                            <p class="vjs-no-js">
                                To view this video please enable JavaScript, and consider upgrading to a
                                web browser that
                                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5
                                    video</a>
                            </p>
                        </video>
                        <canvas v-show="canvasCheckbox" id="drawing-canvas"
                            class="absolute left-0 top-0  z-50 bg-gray-300/30"></canvas>
                        </div>
                    </div>
                    <div class="w-20 text-white">
                        video info
                    </div>
                </div>
                <div id="frame_player" v-show="show == 'frame'" class="w-full h-full">
                    <img :src="frameSrc" :key="frameKey" alt="Processing Frame" class="w-auto h-full mx-auto" />
                </div>
            </div>
            <div class="flex flex-row h-1/4 overflow-y">
                <div class="w-2/4 h-full overflow-y">
                    <div class="flex flex-row" v-if="selectedAnalysis">
                        <input ref="video_input"
                            class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                            @change="uploadVideo" id="file_input" type="file">
                    </div>
                    <ul class="overflow-y-auto h-64">
                        <li v-for="video in video_list" :key="video.id">
                            <a @click="selectVideo(video)">{{ video.name }}</a>
                        </li>
                    </ul>
                </div>
                <div class="w-1/4">
                    <div class="flex items-center ">
                        <input id="default-radio-1" type="radio" value="stab_vid" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="default-radio-1"
                            class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Stablize Vidstab</label>
                    </div>
                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="stab_of" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="default-radio-2"
                            class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Crop ROI</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="stab_of" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="default-radio-2"
                            class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Set drillhole</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="stab_of" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="default-radio-2"
                            class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Flyrock analysis</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="stab_of" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                        <label for="default-radio-2"
                            class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Smoke analysis</label>
                    </div>

                </div>
                <div class="w-1/4">
                    <div>
                        <input type="text" class="text-black" v-model="operationOptions.input_path"
                            placeholder="input_path" required />
                    </div>
                    <div>
                        <input type="text" class="text-black" v-model="operationOptions.output_path"
                            placeholder="output_path" required />
                    </div>

                    <div v-if="selectedOperation == 'stab_vid'">

                    </div>
                </div>
                <div class="w-1/4">
                    <button @click="runOperation()">Run</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import api from '@/services/api';
import config from '@/config';

export default {
    data() {
        return {
            analysis_name: "",
            analysis_list: [],
            video_list: [],
            selectedAnalysis: null,
            selectedVideo: null,
            playingVideo: "",
            frameSrc: "",
            player: null,
            selectedOperation: null,
            show: 'video',
            canvasCheckbox: false,
            drawType: 'point',
            frameKey: 0,  // Key to force re-rendering of the image
            videoSetupOptions: JSON.stringify({
                autoplay: false,
                controls: true,
                preload: 'auto',
            }),
            operationOptions: {
                input_path: "",
                output_path: "",
                stab_vid: {

                }
            },
            drawing: false,
            shapes: []
        }

    },
    mounted() {
        this.getAnalysis()
        try {
            this.player = videojs("#my-video", {}, function onPlayerReady() {
                console.log('onPlayerReady', this);
            });
        } catch (err) {
            console.log(err)
        }

        this.connectWebSocket();
    },
    watch: {
        selectedVideo() {
            if (this.selectedVideo) {
                this.show = 'video'
                this.playingVideo = this.getVideoUrl(this.selectedVideo)
                this.$nextTick(() => {
                    this.player.src({ type: 'video/mp4', src: this.playingVideo });
                    this.player.load();
                    this.player.on('loadeddata', () => {
                        this.player.play();
                    })
                });
            }
        },
        canvasCheckbox() {
            if (this.canvasCheckbox) {
                this.resizeCanvas();
                this.setupCanvas();
            }
        }
    },
    methods: {
        getVideoUrl(video) {
            return `${config.backendUrl}/video/${this.selectedAnalysis}/${video.name}`
        },
        selectVideo(video) {
            this.selectedVideo = video
        },
        selectOperation(operation) {
            this.selectedOperation = operation
        },
        async uploadVideo() {
            alert(1)
            try {
                let resp = await api.uploadVideo(this.selectedAnalysis, this.$refs.video_input.files[0])
                this.getVideos(this.selectedAnalysis)
            } catch (err) {
                console.error(err)
            }
        },
        async runOperation() {
            try {
                this.show = 'frame'
                let resp = await api.runOperation(this.selectedAnalysis, this.selectedOperation, this.operationOptions)
                if (resp.code == '000') {
                    if(this.operationOptions.output_path){
                        this.show = 'video'
                        this.frameSrc = `${config.backendUrl}/video/${this.selectedAnalysis}/${this.operationOptions.output_path}`
                        this.getVideos(this.selectedAnalysis)                
                    }
                }
            } catch (err) {
                console.error(err)
            }
        },
        async getAnalysis() {
            try {
                let resp = await api.getAnalysis()
                this.analysis_list = resp.data
            } catch (err) {
                console.error(err)
            }
        },
        async createHandler() {
            try {
                await api.createAnalysis(this.analysis_name)
                let resp = await api.getAnalysis()
                this.analysis_list = resp.data
            } catch (err) {
                console.error(err)
            }
        },
        async getVideos(analysis_id) {
            try {
                this.selectedAnalysis = analysis_id
                let resp = await api.getVideos(analysis_id)
                this.video_list = resp.data

            } catch (err) {
                console.error(err)
            }
        },
        connectWebSocket() {
            const ws = new WebSocket(config.backendUrlWs);
            ws.onmessage = (event) => {
                this.frameSrc = `data:image/jpeg;base64,${event.data}`;
                this.frameKey += 1;  // Update the key to force re-rendering
            };
            ws.onclose = () => {
                console.log('WebSocket connection closed');
            };
        },
        resizeCanvas() {
            const video = document.getElementById('my-video');
            const canvas = document.getElementById('drawing-canvas'); 
            canvas.x = video.x;
            canvas.y = video.y;
            canvas.width = video.clientWidth;
            canvas.height = video.clientHeight;
        },
        setupCanvas() {
            const canvas = document.getElementById('drawing-canvas');
            const ctx = canvas.getContext('2d');
            let startX, startY;

            canvas.addEventListener('mousedown', (e) => {
                console.log('mousedown');
                this.drawing = true;
                const rect = e.target.getBoundingClientRect();
                startX = e.clientX - rect.left;
                startY = e.clientY - rect.top;
                console.log(startX, startY);
            });

            canvas.addEventListener('mousemove', (e) => {
                if (this.drawing) {
                    const rect = e.target.getBoundingClientRect();
                    const currentX = e.clientX - rect.left;
                    const currentY = e.clientY - rect.top;
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.beginPath();
                    ctx.rect(startX, startY, currentX - startX, currentY - startY);
                    ctx.stroke();
                }
            });

            canvas.addEventListener('mouseup', (e) => {
                console.log('mouseup');
                console.log(e.offsetX, e.offsetY);
                if (this.drawing) {
                    this.drawing = false;
                    const rect = e.target.getBoundingClientRect();
                    const currentX = e.clientX - rect.left;
                    const currentY = e.clientY - rect.top;
                    this.shapes.push({
                        type: 'rectangle',
                        startX,
                        startY,
                        width: currentX - startX,
                        height: currentY - startY
                    });
                    console.log(this.shapes);
                }
            });
        },
        saveShapes() {
            const json = JSON.stringify(this.shapes);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'shapes.json';
            a.click();
            URL.revokeObjectURL(url);
        }
    },
    beforeDestroy() {
        if (this.player) {
            this.player.dispose();
        }
    }
}
</script>

<style scoped>
#drawing-canvas {
    position: absolute;
    top: 0;
    left: 0;
    /* pointer-events: none; */
    /* Prevent interfering with video controls */
}
</style>