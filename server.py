import json
import os
import shutil
from typing import Union

import uvicorn
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException

from config import Config
from data_handler import DataHandler

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    handler = DataHandler(websocket)

    try:
        while True:
            data_type = await websocket.receive_text()
            print("data_type = " + data_type)

            if data_type == "text":
                text_data = await websocket.receive_text()
                await handler.handle_text(text_data)
            if data_type == "message":
                text_data = await websocket.receive_text()
                await handler.handle_message(text_data)
            if data_type == "json":
                json_data = await websocket.receive_text()
                await handler.handle_json(json.loads(json_data))
            if data_type == "audio":
                binary_data = await websocket.receive_bytes()
                await handler.handle_audio(binary_data)

            if data_type == "image":
                binary_data = await websocket.receive_bytes()
                await handler.handle_image(binary_data)

    except Exception as e:
        print(e)
        await websocket.close()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}


async def send_data(websocket: WebSocket, data: Union[str, bytes]):
    if isinstance(data, str):
        await websocket.send_text(data)
    elif isinstance(data, bytes):
        await websocket.send_bytes(data)
    else:
        raise HTTPException(status_code=400, detail="Invalid data type")


if __name__ == "__main__":

    # audioフォルダを削除して作成
    shutil.rmtree("audio")
    os.makedirs("audio", exist_ok=True)
    os.makedirs("history", exist_ok=True)

    config = Config()
    if config.use_ssl:
        uvicorn.run(app, host=config.host, port=config.port, ssl_keyfile=config.ssl_keyfile,
                    ssl_certfile=config.ssl_certfile)
    else:
        uvicorn.run(app, host=config.host, port=config.port)
