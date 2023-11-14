import json
import asyncio
import websockets
import ssl
from websockets import WebSocketServerProtocol

from media_data_handler import MEDIA_TYPE_IMAGE, MEDIA_TYPE_AUDIO, MEDIA_TYPE_JSON


class WebSocketServer:
    def __init__(self, config_file, data_handler):
        with open(config_file) as file:
            self.config = json.load(file)

        self.data_handler = data_handler
        self.path = self.config["server_path"]
        self.ssl_context = None
        if self.config["use_ssl"]:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(self.config["ssl_cert"], self.config["ssl_key"])

    async def handler(self, websocket: WebSocketServerProtocol, path: str):

        # クライアントが接続したことを検出
        client_address = websocket.remote_address
        print(f"New connection: {client_address}")

        try:
            async for message in websocket:
                # メッセージの最初のバイトをメディアタイプとして使用
                media_type = message[0]
                if media_type == MEDIA_TYPE_JSON:  # JSONデータのヘッダー
                    await self.data_handler.handle_json(message[1:], websocket)
                elif media_type == MEDIA_TYPE_AUDIO:  # 音声データのヘッダー
                    await self.data_handler.handle_audio_data(message[1:], websocket)
                elif media_type == MEDIA_TYPE_IMAGE:  # 画像データのヘッダー
                    await self.data_handler.handle_image_data(message[1:], websocket)
                else:
                    await self.data_handler.handle_text_message(message, websocket)

                #print(f"Received message from {client_address}: {message}")
                #await websocket.send(message)
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed with {client_address}, code: {e.code}, reason: {e.reason}")


    def run(self):
        start_server = websockets.serve(
            self.handler,
            self.config["server_ip"],
            self.config["port_no"],
            ssl=self.ssl_context,
        )
        print("websocket server start " + self.config["server_ip"] + ":" + str(self.config["port_no"]))
        print("ssl:" + str(self.config["use_ssl"]))
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
        print("websocket server end")
