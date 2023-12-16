import io
import json
import time
import wave
import pyaudio
import requests

class Voicevox:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port

    def synthesize(self, text, filename):
        params = (
            ("text", text),
            ("speaker", 47)  # 音声の種類をInt型で指定
        )

        # 音声合成用のクエリ作成
        query = requests.post(
            f'http://{self.host}:{self.port}/audio_query',
            params=params
        )

        # 音声合成を実施
        result = requests.post(
            f'http://{self.host}:{self.port}/synthesis',
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(query.json())
        )

        if result.status_code != 200:
            print("Error: " + result.status_code)
            print(result.json())
            return

        # wavファイルとして保存
        with open(filename, 'wb') as f:
            f.write(result.content)



    def speak(self, text=None, speaker=47):  # VOICEVOX:ナースロボ＿タイプＴ

        params = (
            ("text", text),
            ("speaker", speaker)  # 音声の種類をInt型で指定
        )

        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )

        # メモリ上で展開
        audio = io.BytesIO(res.content)

        with wave.open(audio, 'rb') as f:
            # 以下再生用処理
            p = pyaudio.PyAudio()

            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)

            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            stream_callback=_callback)

            # Voice再生
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()
