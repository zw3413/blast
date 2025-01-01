import os
from typing import Annotated
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException,  File, Form, UploadFile, WebSocket
from typing import List
from .schemas import *
from ..func.methods import *
from ..func.operations import *
from ..func.queue_storage import frame_queue
import asyncio

router = APIRouter()

temp_path = os.path.join(os.getcwd(), "temp")

# Background task for sending frames via WebSocket
async def send_frames(websocket: WebSocket, frame_queue: asyncio.Queue):
    try:
        while True:
            if not frame_queue.empty():
                frame_base64 = await frame_queue.get()
                await websocket.send_text(frame_base64)  # Send the frame via WebSocket
                await asyncio.sleep(0.001)
            else:    
                await asyncio.sleep(0.1)  # Avoid busy-waiting
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  
    asyncio.create_task(send_frames(websocket, frame_queue))
    await websocket.receive_text()

@router.post("/upload_video")
async def upload_video(file : Annotated[bytes, File()], name: Annotated[str, Form()], ana_id:Annotated[str, Form()]):
    file_path = os.path.join(temp_path, ana_id, name)  # Save in a folder
    with open(file_path, "wb") as f:
        f.write(file)
    return {"msg": "", "code": "000"}


@router.post("/run_operation")
async def run_operation(operation: Operation):
    try:
        if operation.op == "stab_vid":
            await stabilize_vidstab(
                os.path.join(
                    temp_path, operation.ana_id, operation.options["input_path"]
                ),
                os.path.join(
                    temp_path, operation.ana_id, operation.options["output_path"]
                ))
       
        elif operation.op == "roi":
            pass
        return {"msg": "", "code": "000"}
    except Exception as e:
        return {"msg": str(e), "code": "001"}


@router.post("/create_analysis")
def create_analysis(ana: Analysis):
    try:
        dir_path = os.path.join(temp_path, ana.name)
        os.makedirs(dir_path)
        return {"msg": "", "code": "000"}
    except Exception as e:
        return {"msg": str(e), "code": "001"}


@router.get("/list_analysis")
def list_analysis():
    try:
        analysis = []
        for dir in os.listdir(temp_path):
            if os.path.isdir(os.path.join(temp_path, dir)):
                analysis.append({"name": dir, "id": dir})
        return {"msg": "", "code": "000", "data": analysis}
    except Exception as e:
        return {"msg": str(e), "code": "001"}


@router.get("/list_videos/{ana_id}")
def list_videos(ana_id: str):
    try:
        videos = []
        for video in os.listdir(os.path.join(temp_path, ana_id)):
            videos.append({"name": video})
        return {"msg": "", "code": "000", "data": videos}
    except Exception as e:
        return {"msg": str(e), "code": "001"}


@router.get("/video/{ana_id}/{video_name}")
async def get_video(ana_id: str, video_name: str):
    file_path = os.path.join(temp_path, ana_id, video_name)
    print(file_path)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    else:
        raise HTTPException(status_code=404, detail="Video not found")
