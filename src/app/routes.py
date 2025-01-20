import os
from typing import Annotated
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, HTTPException, Response, Header, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import List
from .schemas import *
from ..func.methods import *
from ..func.operations import *
sys.path.append(os.path.join(os.getcwd(),"src"))
from func.queue_storage import FrameQueueSingleton
from ..func.ffmpeg_tools import get_video_info_ffmpeg
import asyncio
import aiofiles
from pathlib import Path
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
        print(f"WebSocket connection encountered an error: {e}")
        # No further action; allow websocket_endpoint to handle disconnection.

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        print("ws: connected")
        frame_queue = FrameQueueSingleton.get_queue()
        print("ws:", frame_queue.qsize())
        print(f"Queue ID: {id(frame_queue)}")
        print(f"Event loop ID: {id(asyncio.get_event_loop())}")
        await send_frames(websocket, frame_queue)
    except WebSocketDisconnect as e:
        print("WebSocket disconnected.")
    except Exception as e:
        print(f"Unexpected WebSocket error: {e}")
    finally:
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close()
        except Exception as e:
            print(f"Error while closing WebSocket: {e}")

@router.post("/upload_video")
async def upload_video(file : Annotated[bytes, File()], name: Annotated[str, Form()], ana_id:Annotated[str, Form()]):
    file_path = os.path.join(temp_path, ana_id, name)  # Save in a folder
    with open(file_path, "wb") as f:
        f.write(file)
    return {"msg": "", "code": "000"}

@router.post("/run_operation")
async def run_operation(operation: Operation):
    try:
        input, output = getInputOutputPath(operation)
        if operation.op == "stab_vid":  
            await stabilize_vidstab(input,output)
        elif operation.op == "crop_roi":
            output_path = operation.options["output_path"]
            withROI = operation.options["withROI"]
            if output_path is None or output_path=="":
                output_path = add_suffix_to_filename(operation.options["input_path"], "crop")
                if withROI :
                    output_path = add_suffix_to_filename(output_path,"ROI", "")
            print(output_path)
            output = os.path.join(temp_path, operation.ana_id, output_path)
            await crop_roi( input,output,operation.options["shape"], withROI )
        elif operation.op == "set_pixel":
            file_path = Path(output)
            # Replace suffix with a new one
            new_file_path = file_path.with_suffix(".json")
            await set_pixel(input, new_file_path)
        elif operation.op == "slungshot":
            await slungshot(input, output, operation.options)
        elif operation.op == "smoke":
            await smoke(input, output, operation.options)
        else:
            print("unknown operation ")
            print(operation)
            return {"msg":"unknow operation", "code":"002"}
        return {"msg": "", "code": "000"}
    except Exception as e:
        print(e)
        return {"msg": str(e), "code": "001"}
    finally:
        print("run operation")


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
        subfolders = [
            {"name":entry,"id":entry} for entry in os.listdir(temp_path) if os.path.isdir(os.path.join(temp_path, entry))
        ]
        # Sort subfolders by creation time
        sorted_subfolders = sorted(subfolders, key=lambda folder: os.path.getctime(os.path.join(temp_path, folder['name'])) , reverse=True)
        return {"msg": "", "code": "000", "data": sorted_subfolders}
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


# @router.get("/video/{ana_id}/{video_name}")
# async def get_video(ana_id: str, video_name: str):
#     file_path = os.path.join(temp_path, ana_id, video_name)
#     print(file_path)
#     if os.path.exists(file_path):
#         return FileResponse(file_path, media_type="video/mp4")
#     else:
#         raise HTTPException(status_code=404, detail="Video not found")

@router.get("/video/{ana_id}/{video_name}")
async def video_endpoint(ana_id: str, video_name: str, range: str = Header(None)):
    file_path = os.path.join(temp_path, ana_id, video_name)
    
    try:
        file_size = os.path.getsize(file_path)
        
        headers = {
            'Accept-Ranges': 'bytes',
            'Content-Type': 'video/mp4'
        }
        
        async with aiofiles.open(file_path, mode='rb') as video_file:
            if not range:
                content = await video_file.read()
                return Response(content, headers=headers)
            
            start, end = range.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
            
            await video_file.seek(start)
            chunk = await video_file.read(end - start + 1)
            
            headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            headers['Content-Length'] = str(end - start + 1)
            return Response(chunk, status_code=206, headers=headers)
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
    
def getInputOutputPath(operation):
    if operation.options["input_path"] is not None :
        
        input = os.path.join(
                        temp_path, operation.ana_id, operation.options["input_path"]
                    )
        if operation.options["output_path"] is None or operation.options["output_path"] == '':
            output_path = add_suffix_to_filename(operation.options["input_path"], to_camel(operation.op))
        else:
            output_path = operation.options["output_path"]
        output = os.path.join(temp_path, operation.ana_id, output_path)
        return input, output

    else :
        if operation.options["output_path"] is None or operation.options["output_path"] == '':
            return None, None
        else:
            output = os.path.join(
                temp_path, operation.ana_id, operation.options["output_path"]
            )
            return None, output
    
def to_camel(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))