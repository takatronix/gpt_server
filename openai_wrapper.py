import json
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

    def load_config(self):
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")

    def query(self, prompt, config_name):
        try:
            config = self.config[config_name]

            # メッセージのリストを初期化
            messages = []

            # configにカスタム指示が存在する場合、それをメッセージに追加
            if "custom_instructions" in config and config["custom_instructions"]:
                custom_instructions = config["custom_instructions"]
                messages.append({"role": "system", "content": custom_instructions})
            # プロンプトをユーザーメッセージとして追加
            messages.append({"role": "user", "content": prompt})

            # APIリクエストを送信
            response = self.client.chat.completions.create(
                model=config["engine"],
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
            )
            token = response.usage.total_tokens

            # 応答を返す
            return response.choices[0].message.content + f"({token} tokens)"
        except Exception as e:
            return str(e)

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

