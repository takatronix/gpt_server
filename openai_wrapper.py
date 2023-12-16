import json
import time

import requests
import uuid
from openai import OpenAI


class OpenAIWrapper:
    def __init__(self, api_key, config_file="openai_wrapper.json"):
        self.api_key = api_key
        self.config_file = config_file
        self.client = OpenAI()
        self.client.api_key = self.api_key
        self.load_config()
        self.session_id = str(uuid.uuid4())  # セッションIDを生成
        self.history = []

    def add_history(self, speaker, text, time=None):
        self.history.append(f"{speaker}: {text}")

        # セッションIDのhistoryファイルに追記
        with open(f"history/{self.session_id}.txt", "a", encoding="utf-8") as file:
            file.write(f"{speaker}: {text}\n")

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")

    async def query(self, prompt, config_name):
        try:
            config = self.config[config_name]

            # メッセージのリストを初期化
            messages = []
            recent_history = []

            # 会話の履歴を追加

            # configにカスタム指示が存在する場合、それをメッセージに追加
            if "custom_instructions" in config and config["custom_instructions"]:
                messages.append({"role": "system", "content": config["custom_instructions"]})

            # 最新のmax_history個のメッセージを追加
            if len(self.history) > config["max_history"]:
                recent_history = self.history[-config["max_history"]:]
            else:
                recent_history = self.history

            for history_message in recent_history:
                role, text = history_message.split(': ', 1)
                messages.append({"role": role, "content": text})


            # 現在のユーザーの入力を追加
            messages.append({"role": "user", "content": prompt})


            #print(messages)
            start_time = time.time()
            # APIリクエストを送信
            response = self.client.chat.completions.create(
                model=config["engine"],
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
            )
            lapse_time = time.time() - start_time
            lapse_time = round(lapse_time, 2)
            token = response.usage.total_tokens

            # 応答を返す
            return response.choices[0].message.content, token, lapse_time
        except Exception as e:
            return str(e), 0, 0

    # (alloy, echo, fable, onyx, nova, shimmer)

    def text_to_speech_stream(self, text, model="tts-1", voice="shimmer", format="mp3"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,  # tts-1
            "input": text,
            "voice": voice,  # alloy, echo, fable, onyx, nova, shimmer
            "format": format  # mp3,opus,aac,flac
        }

        # OpenAI TTS APIエンドポイントへのリクエストを送信
        response = requests.post("https://api.openai.com/v1/audio/speech", headers=headers, json=data, stream=True)
        print(response)
        if response.status_code == 200:
            # レスポンスをチャンク単位で処理
            for chunk in response.iter_content(chunk_size=1024):
                yield chunk
        else:
            raise Exception(f"Failed to retrieve audio stream: {response.status_code}")

    def synthesize(self, text, speech_file_path, model="tts-1", voice="shimmer"):

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        response.stream_to_file(speech_file_path)
