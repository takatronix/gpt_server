import os
import shutil

from config import Config
from media_data_handler import MediaDataHandler
from websocket_server import WebSocketServer

# pip install torch==2.1.0+cu118 -f https://download.pytorch.org/whl/torch_stable.html

if __name__ == "__main__":
    # 使用例
    config = Config('config.json')

    # 起動時に/audioフォルダの中身を削除

    shutil.rmtree("audio")
    os.makedirs("audio", exist_ok=True)

    os.makedirs("history", exist_ok=True)


    handler = MediaDataHandler(config)
    server = WebSocketServer("config.json", handler)
    server.run()
