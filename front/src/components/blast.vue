<template>
    <div class="flex flex-row w-full min-h-screen max-h-screen overflow-hidden text-white">
        <div class="flex flex-col h-screen w-60 ">
            <img src="/cotegold.png" alt="logo" class=" w-full" />
            <ul
                class="flex flex-col h-full space-y-1 p-2 border-r-2 border-gray-800 overflow-y-auto divide-y divide-gray-800 scrollbar">
                <li v-for="analysis in analysis_list" :key="analysis.id" class="p-2 flex items-center ">
                    <a class="flex text-gray-300 cursor-pointer" @click="getFiles(analysis.id)"> {{ analysis.name }}</a>
                </li>
            </ul>

            <div class="flex flex-col space-y-2  justify-end">
                <div class="flex flex-row h-8 justify-end ">
                    <input type="text" class="text-black p-2" v-model="analysis_name">
                    <button type="button" @click="createHandler" class="ml-auto text-white">create</button>
                </div>
              
                <img src="/gdg.png" alt="logo" class=" w-full" />
                <img src="/laurentian.svg" alt="logo" class=" w-full bg-white" />
            </div>
        </div>

        <div class="w-full h-screen">

            <div class="h-4/5 " id="default-tab-content">
                <div class="mb-2 border-b border-gray-200 h-1/10 ">
                    <ul class="flex flex-wrap justify-end -mb-px text-sm font-medium text-center" id="default-tab"
                        data-tabs-toggle="#default-tab-content" role="tablist">
                        <li class="me-2" role="presentation">
                            <button
                                class="inline-block p-2 border-b-2 rounded-t-lg hover:text-gray-600 hover:border-gray-300 "
                                id="VideoPlayer-tab" data-tabs-target="#VideoPlayer" type="button" role="tab"
                                aria-controls="VideoPlayer" :aria-selected="show == 'video'">VideoPlayer</button>
                        </li>
                        <li class="me-2" role="presentation">
                            <button
                                class="inline-block p-2 border-b-2 rounded-t-lg hover:text-gray-600 hover:border-gray-300 "
                                id="frame_player-tab" data-tabs-target="#frame_player" type="button" role="tab"
                                aria-controls="frame_player" :aria-selected="show == 'frame'">ProcessingMonitor</button>
                        </li>

                    </ul>
                </div>
                <div class="hidden rounded-lg h-9/10  w-full  flex flex-row overflow-y-auto" id="VideoPlayer"
                    role="tabpanel" aria-labelledby="VideoPlayer-tab">
                    <div class="flex flex-col p-1 space-y-2 w-20 text-left items-center">
                        <input type="checkbox" class="mt-10" v-model="canvasCheckbox" />Draw
                        <input type="text" class="text-black w-full" v-model="current_pixel.x" placeholder="x" />
                        <input type="text" class="text-black w-full" v-model="current_pixel.y" placeholder="x" />
                        <!-- <button class="flex" @click="drawType = 'point'">point</button>
                        <button class="flex" @click="drawType = 'line'">line</button> -->
                        <button class="flex" @click="drawType = 'rect'">rect</button>
                        <button class="flex" @click="drawType = 'circle'">circle</button>
                        <button class="flex" @click="drawType = 'point'">point</button>
                        <button class="flex" @click="clearCanvas">clear</button>
                        <button class="flex" @click="uploadShpaes">Save</button>
                    </div>
                    <div
                        class="flex flex-col max-h-full w-full flex-shrink-1 min-w-[100px] overflow-x-hidden items-center grid place-items-center">
                        <div ref="video_container" class=" w-full relative ">

                            <video id="my-video"
                                class="z-0 video-js items-center vjs-default-skin w-full max-h-full justify-middle object-contain"
                                controls preload="auto" :data-setup="videoSetupOptions" @loadedmetadata="resizeCanvas">
                                <source :src="playingVideo" type="video/mp4" />
                                <p class="vjs-no-js z-0">
                                    To view this video please enable JavaScript, and consider upgrading to a
                                    web browser that
                                    <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5
                                        video</a>
                                </p>
                            </video>
                            <canvas v-show="canvasCheckbox" id="drawing-canvas"
                                class="absolute left-0 top-0  z-10 bg-gray-300/30 "></canvas>

                        </div>
                    </div>
                    <div class="flex flex-col text-white w-[500px] items-center justify-center">
                        video info
                    </div>
                </div>

                <div id="frame_player" class="hidden p-4 rounded-lg  flex flex-row w-full h-full overflow-none"
                    role="tabpanel" aria-labelledby="frame_player-tab">
                    <div class=" min-w-20 ">  </div>
                    <div>
                        
                    <img :src="frameSrc" ref="frame_img" :key="frameKey" alt="Processing Frame"
                        class="flex-shrink-1   justify-left object-contain w-full max-h-full object-contain" />
                </div>
                
                    <div class="flex flex-col text-white w-[500px] items-center justify-center"></div>
                </div>
            </div>
<!--operations-->
            <div class="flex flex-row h-1/5  z-20 border-t-2 border-gray-800">
                <div class="w-1/5"></div>
                <div class="w-1/5 p-2">
                    <div class="flex items-center ">
                        <input id="default-radio-1" type="radio" value="stab_vid" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500   focus:ring-2  ">
                        <label for="default-radio-1" class="ms-2 text-sm font-medium text-gray-300 ">Stablize
                            Vidstab</label>
                    </div>
                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="crop_roi" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500   focus:ring-2  ">
                        <label for="default-radio-2" class="ms-2 text-sm font-medium text-gray-300 ">Crop ROI</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="set_pixel" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500  focus:ring-2 ">
                        <label for="default-radio-2" class="ms-2 text-sm font-medium text-gray-300 ">Set Pixel</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="slungshot" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500   focus:ring-2  ">
                        <label for="default-radio-2" class="ms-2 text-sm font-medium text-gray-300 ">Slungshot</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="fragmentation"
                            v-model="selectedOperation" name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500   focus:ring-2  ">
                        <label for="default-radio-2" class="ms-2 text-sm font-medium text-gray-300 ">Fragmentation</label>
                    </div>

                    <div class="flex items-center">
                        <input checked id="default-radio-2" type="radio" value="smoke" v-model="selectedOperation"
                            name="selectedOperation"
                            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500   focus:ring-2  ">
                        <label for="default-radio-2" class="ms-2 text-sm font-medium text-gray-300 ">Smoke</label>
                    </div>

                </div>
                <div class="w-1/5 p-2 space-y-2">
                    <div v-for="param in selectedOperationParams" :key="param.name">

                        <input v-if="param.type == 'input'" type="text" class="text-black"
                            v-model="operationOptions[param.name]" :placeholder="param.description" required />

                        <div v-if="param.type == 'combobox'">
                            <label>{{ param.description }} </label>
                            <select class="text-black ml-2 w-20" v-model="operationOptions[param.name]">
                                <option v-for="option in param.options" :key="option" :value="option">{{ option }}
                                </option>
                            </select>
                        </div>

                    </div>
                    <button :disabled="run_disabled == true" @click="runOperation()">{{ run_btn_text }}</button>

                </div>
                <div class="w-2/5 h-full p-2 overflow-y-auto scrollbar">
                    <div class="flex flex-row" v-if="selectedAnalysis">
                        <input ref="video_input"
                            class="block w-100 text-xs text-gray-800 border border-gray-300 rounded-lg cursor-pointer bg-gray-50  focus:outline-none   "
                            @change="uploadVideo" id="file_input" type="file">
                    </div>
                    <ul class="">
                        <li v-for="file in file_list" :key="file.id">
                            <a @click="selectFile(file)" class="cursor-pointer text-gray-300">{{ file.name }}</a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        <div class="fixed bottom-0 right-0"></div>
    </div>
</template>

<script>
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import api from '@/services/api';
import config from '@/config';
import { layer } from '@layui/layui-vue';
import { nextTick, ref } from 'vue';
import { initFlowbite } from 'flowbite'

export default {
    data() {
        return {
            analysis_name: "",
            analysis_list: [],
            file_list: [],
            selectedAnalysis: null,
            selectedVideo: null,
            selectedShapes: null,
            selectedVideo_info: null,
            playingVideo: "",
            frameSrc: "",
            player: null,
            selectedOperation: 'stab_vid',
            selectedOperationParams: null,
            show: 'video',
            canvasCheckbox: false,
            drawType: 'point',
            frameKey: 0,  // Key to force re-rendering of the image
            run_disabled: false,
            run_btn_text: "Run",
            videoSetupOptions: JSON.stringify({
                autoplay: false,
                controls: true,
                preload: 'auto',
            }),
            operationOptions: {
                input_path: "",
                output_path: "",
                shape_str: "",
                stab_vid: {

                }
            },
            drawing: false,
            shapes: ref([]),
            zoom_ratio: null,
            current_pixel: {
                x: 0,
                y: 0
            },

        }

    },
    mounted() {
        initFlowbite();
        this.getAnalysis()
        try {
            this.player = videojs("#my-video", {
                fluid: true
            }, function onPlayerReady() {
                console.log('onPlayerReady', this);
            });
        } catch (err) {
            console.log(err)
        }
        //this.resizeVideo()
        this.connectWebSocket();
    },
    watch: {
        show() {
            if (this.show == 'frame') {
                document.getElementById("frame_player-tab").click()
            } else if (this.show == 'video') {
                document.getElementById("VideoPlayer-tab").click()
            }
        },
        selectedVideo() {
            //this.resizeVideo()
            if (this.selectedVideo) {
                this.show = 'video'
                this.playingVideo = this.getVideoUrl(this.selectedVideo)
                this.$nextTick(() => {
                    this.player.src({ type: 'video/mp4', src: this.playingVideo });
                    this.player.load();
                    this.player.on('loadeddata', () => {
                        //this.resizeVideo()
                        this.player.play();
                    })
                    this.getSelectedVideoInfo()
                });
            }
        },
        selectedShapes() {
            if (this.selectedShapes) {
                api.getFile(this.selectedAnalysis, this.selectedShapes.name).then((resp) => {
                    this.clearCanvas();
                    this.shapes = this.cvtCanvasPixelValues(resp, this.zoom_ratio);
                }).catch((err) => {
                    console.error(err)
                })
            }
        },
        shapes() {
            this.canvasCheckbox = true
            this.$nextTick(() => {
                if (this.shapes && this.shapes.length > 0) {
                    this.drawShapes(this.shapes);
                }
            });
        },
        canvasCheckbox() {
            if (this.canvasCheckbox) {
                this.resizeCanvas();
                this.setupCanvas();
            }
        },
        selectedOperation(operation) {
            this.selectedOperationParams = config.operationParamter[operation];
        },
    },
    methods: {
        resizeVideo() {
            if (this.selectedVideo == null) {

                this.player.width(this.$refs.video_container.clientWidth)
                this.player.height(this.$refs.video_container.clientHeight)
            } else {
                //this.player.width(this.$refs.video_container.clientWidth)

                this.player.height(this.$refs.video_container.clientHeight)
            }
        },
        getSelectedVideoInfo() {
            api.getVideoInfo(this.selectedAnalysis, this.selectedVideo.name).then((resp) => {
                this.selectedVideo_info = resp.data
                const video_width = this.selectedVideo_info.width
                const display_width = this.player.currentWidth()
                this.zoom_ratio = video_width / display_width
            }).catch((err) => {
                console.error(err)
            })
        },
        getVideoUrl(video) {
            return `${config.backendUrl}/video/${this.selectedAnalysis}/${video.name}`
        },
        selectFile(file) {
            this.operationOptions.input_path = file.name
            const suffix = file.name.split('.')[file.name.split('.').length - 1].toLowerCase()
            if (suffix == 'mp4') {
                this.selectedVideo = file
            } else if (suffix == 'json') {
                this.selectedShapes = file
            }
        },
        async uploadVideo() {
            try {
                let resp = await api.uploadVideo(this.selectedAnalysis, this.$refs.video_input.files[0])
                this.getFiles(this.selectedAnalysis)
            } catch (err) {
                console.error(err)
            }
        },
        async runOperation() {
            this.run_disabled = true
            this.run_btn_text = "Running"
            try {
                if (this.selectedOperation == 'stab_vid') {

                } else if (this.selectedOperation == 'crop_roi') {

                    if (!this.operationOptions.shape_str || this.operationOptions.shape_str.length == 0) {
                        alert('Please draw the shape or select a shape first')
                        return
                    }
                    this.operationOptions.shape = JSON.parse(this.operationOptions.shape_str)
                    this.show = 'frame'
                } else if (this.selectedOperation == 'set_pixel') {
                    const csvName = this.operationOptions.drill_hole_data
                }
                let resp = await api.runOperation(this.selectedAnalysis, this.selectedOperation, this.operationOptions)
                if (resp.code == '000') {
                    this.show = 'video'
                    if (this.operationOptions.output_path) {
                        this.frameSrc = `${config.backendUrl}/video/${this.selectedAnalysis}/${this.operationOptions.output_path}`
                        this.getFiles(this.selectedAnalysis)
                    } else if (this.operationOptions.input_path) {
                        this.frameSrc = `${config.backendUrl}/video/${this.selectedAnalysis}/${this.operationOptions.input_path}`
                        this.getFiles(this.selectedAnalysis)
                    }
                }

            } catch (err) {
                console.error(err)
            } finally {
                this.run_disabled = false
                this.run_btn_text = "Run"
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
        async getFiles(analysis_id) {
            try {
                this.selectedAnalysis = analysis_id
                let resp = await api.getFiles(analysis_id)
                this.file_list = resp.data

            } catch (err) {
                console.error(err)
            }
        },
        base64ToBlob(base64String) {
            // Remove data URL prefix if present
            const base64Data = base64String.replace(/^data:image\/(png|jpeg|jpg);base64,/, '');

            // Convert base64 to binary
            const binaryString = window.atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);

            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }

            // Create and return Blob
            return new Blob([bytes], { type: 'image/jpeg' });
        },
        connectWebSocket() {
            const ws = new WebSocket(config.backendUrlWs);
            console.log("WebSocket connected.")
            const imgElement = this.$refs.frame_img
            ws.onmessage = (event) => {
                console.log("WebSocket msg received")
                // if (this.show != 'frame') {
                //     this.show = 'frame'
                // }
                URL.revokeObjectURL(imgElement.src);
                this.frameSrc = `data:image/jpeg;base64,${event.data}`;
                this.frameKey += 1;  // Update the key to force re-rendering
            };
            ws.onclose = () => {
                console.log('WebSocket connection closed');
                setTimeout(() => {
                    this.connectWebSocket();
                }, 1000);
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
                if (this.drawType == 'point') {
                    const size = 10
                    const x = startX
                    const y = startY
                    ctx.beginPath();
                    ctx.moveTo(x - size, y);
                    ctx.lineTo(x + size, y);
                    ctx.moveTo(x, y + size);
                    ctx.lineTo(x, y - size);
                    ctx.strokeStyle = 'black'; // Customize color
                    ctx.lineWidth = 2; // Customize line width
                    ctx.stroke();
                    this.shapes.value.push({
                        type: 'point',
                        x: startX,
                        y: startY
                    });
                }
            });

            canvas.addEventListener('mousemove', (e) => {
                const rect = e.target.getBoundingClientRect();
                const currentX = e.clientX - rect.left;
                const currentY = e.clientY - rect.top;
                this.current_pixel = this.cvtRealPixelValues_point({ x: currentX, y: currentY }, this.zoom_ratio)
                if (this.drawing) {
                    if (this.drawType == 'rect') {
                        ctx.clearRect(startX, startY, currentX - startX, currentY - startY);
                        ctx.beginPath();
                        ctx.rect(startX, startY, currentX - startX, currentY - startY);
                        ctx.stroke();
                    }
                    else if (this.drawType == 'circle') {
                        const radius = Math.sqrt((currentX - startX) ** 2 + (currentY - startY) ** 2);
                        ctx.clearRect(startX - radius, startY - radius, currentX + radius, currentY + radius);
                        ctx.beginPath();
                        ctx.arc(startX, startY, radius, 0, 2 * Math.PI);
                        ctx.stroke();
                    }
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

                    if (this.drawType == 'rect') {
                        this.shapes.push({
                            type: 'rectangle',
                            x: startX,
                            y: startY,
                            w: currentX - startX,
                            h: currentY - startY
                        });
                        this.operationOptions.shape_str = JSON.stringify(this.cvtRealPixelValues(this.shapes))
                    } else if (this.drawType == 'circle') {
                        this.shapes.value.push({
                            type: 'circle',
                            x: startX,
                            y: startY,
                            r: Math.sqrt((currentX - startX) ** 2 + (currentY - startY) ** 2)
                        });
                    } console.log(this.shapes);
                }
            });
        },
        clearCanvas() {
            const canvas = document.getElementById('drawing-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            this.shapes = [];
            this.selectedShapes = null;
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
        },
        uploadShpaes_Upload(index, name, elem) {
            const shapes = this.cvtRealPixelValues(this.shapes, this.zoom_ratio);
            api.saveShapes(this.selectedAnalysis, this.selectedVideo.name, name, shapes).then((resp) => {
                console.log(resp);
                this.getFiles(this.selectedAnalysis);
            }).catch((err) => {
                console.error(err);
            });
            layer.close(index);
        },
        uploadShpaes() {
            layer.prompt({ title: 'Input Name', formType: 0, placeholder: '', yes: this.uploadShpaes_Upload });

        },
        cvtRealPixelValues(shapes, zoom_ratio) {
            if (!zoom_ratio) {
                zoom_ratio = this.zoom_ratio
            }
            const new_shapes = [];
            for (const shape of shapes) {
                const s = {}
                s.x = Math.round(shape.x * zoom_ratio);
                s.y = Math.round(shape.y * zoom_ratio);
                if (shape.type == 'rectangle') {
                    s.w = Math.round(shape.w * zoom_ratio);
                    s.h = Math.round(shape.h * zoom_ratio);
                } else if (shape.type == 'circle') {
                    s.r = Math.round(shape.r * zoom_ratio);
                }
                s.type = shape.type;
                new_shapes.push(s);
            }
            return new_shapes;
        },
        cvtCanvasPixelValues(shapes, zoom_ratio) {
            const new_shapes = [];
            for (const shape of shapes) {
                const s = {}
                s.x = Math.round(shape.x / zoom_ratio);
                s.y = Math.round(shape.y / zoom_ratio);
                if (shape.type == 'rectangle') {
                    s.w = Math.round(shape.w / zoom_ratio);
                    s.h = Math.round(shape.h / zoom_ratio);
                } else if (shape.type == 'circle') {
                    s.r = Math.round(shape.r / zoom_ratio);
                }
                s.type = shape.type;
                new_shapes.push(s);
            }
            return new_shapes;
        },
        cvtRealPixelValues_point(pixel, zoom_ratio) {
            if (!zoom_ratio) {
                zoom_ratio = this.zoom_ratio
            }
            const new_pixel = {}
            new_pixel.x = Math.round(pixel.x * zoom_ratio);
            new_pixel.y = Math.round(pixel.y * zoom_ratio);
            return new_pixel;
        },
        drawShapes(shapes) {
            const canvas = document.getElementById('drawing-canvas');
            const ctx = canvas.getContext('2d');
            shapes.forEach(shape => {
                try {
                    ctx.fillStyle = shape.color || 'black'; // Default color is black
                    ctx.beginPath();
                    if (shape.type === 'rectangle') {
                        ctx.strokeRect(shape.x, shape.y, shape.w, shape.h);
                    } else if (shape.type === 'circle') {
                        ctx.arc(shape.x, shape.y, shape.r, 0, Math.PI * 2);
                    } else if (shape.type === 'point') {
                        ctx.arc(shape.x, shape.y, 2, 0, 2 * Math.PI);
                    } else {
                        console.warn(`Unknown shape type: ${shape.type}`);
                    }
                    ctx.stroke();
                } catch (err) {
                    console.error(err)
                }
            });
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

input,
select {
    padding-top: 0;
    padding-bottom: 0;
    padding-left: 0;
    padding-right: 0;
    font-size: small
}
</style>