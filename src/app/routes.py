import os
from typing import Annotated
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException,  File, Form, UploadFile, WebSocket
from typing import List
from .schemas import *
from ..func.methods import *
from ..func.operations import *
from ..func.queue_storage import frame_queue
from ..func.ffmpeg_tools import get_video_info_ffmpeg
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
        elif operation.op == "crop_roi":
            await crop_roi(
                os.path.join(
                    temp_path, operation.ana_id, operation.options["input_path"]
                ),
                os.path.join(
                    temp_path, operation.ana_id, operation.options["output_path"]
                ),
                operation.options["shape"]
            )
        elif operation.op == "set_pixel":
            drill_hole_data =operation.options["drill_hole_data"]
            output_name = add_suffix_to_filename(drill_hole_data, "_SetPixel")
            await set_pixel(
                os.path.join(
                    temp_path, operation.ana_id, drill_hole_data
                ),
                os.path.join(
                    temp_path, operation.ana_id, output_name
                ),
            )
        elif operation.op == "slungshot":
              await slungshot(
                os.path.join(
                    temp_path, operation.ana_id, operation.options["input_path"]
                )
            )
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


@router.get("/list_files/{ana_id}")
def list_files(ana_id: str):
    try:
        files = []
        for file in os.listdir(os.path.join(temp_path, ana_id)):
            files.append({"name": file})
        return {"msg": "", "code": "000", "data": files}
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

@router.get("/video_info/{ana_id}/{video_id}")
def get_video_info(ana_id: str, video_id: str):
    file_path = os.path.join(temp_path, ana_id, video_id)
    if os.path.exists(file_path):
        return {"msg": "", "code": "000", "data": get_video_info_ffmpeg(file_path)}
    else:
        return {"msg": "Video not found", "code": "001"}
    
@router.post("/save_shapes")
def save_shapes(shapes: Shapes):
    ana_id = shapes.ana_id
    video_id = shapes.video_id
    name = shapes.name
    shapes = shapes.shapes
    try:
        file_path = os.path.join(temp_path, ana_id, name)
        with open(file_path, "w") as f:
            f.write(shapes)
        return {"msg": "", "code": "000"}
    except Exception as e:
        return {"msg": str(e), "code": "001"}
    
@router.get("/get_file/{ana_id}/{file_name}")
def get_file(ana_id: str, file_name: str):
    file_path = os.path.join(temp_path, ana_id, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")