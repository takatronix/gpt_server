import os
import time
from datetime import datetime

import whisper
from faster_whisper import WhisperModel


def audio_data_to_file(audio_data: bytes):
    received_time = datetime.now()
    filename = received_time.strftime("%Y%m%d%H%M%S") + ".wav"
    filepath = os.path.join("audio", filename)
    # フォルダがなければ作成
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "wb") as f:
        f.write(audio_data)
        # ファイルを確実に書き出すためにflushとfsyncを使用
        f.flush()
        os.fsync(f.fileno())

    # 絶対パスを返す
    return os.path.abspath(filepath)


class SpeechRecognizer:
    def __init__(self, config, recognizer):
        self.device = config.device
        self.recognizer = recognizer
        self.config = config

        if recognizer == "whisper":
            print("loading model from " + config.whisper_model)
            self.model = whisper.load_model(config.whisper_model, device=self.device)
            print("(whisper) model loaded ")

        if recognizer == "faster-whisper":
            print("loading model from " + config.faster_whisper_model)
            self.model = WhisperModel(config.faster_whisper_model, device=self.device, compute_type="float16")
            # 非公式のfaster-whisperV3の場合は
            self.model.feature_extractor.mel_filters = self.model.feature_extractor.get_mel_filters(
                self.model.feature_extractor.sampling_rate, self.model.feature_extractor.n_fft, n_mels=128)
            print("(faster-whisper) model loaded")

    def recognize(self, wav_file):

        if not os.path.exists(wav_file):
            print(f"ファイルが見つかりません: {wav_file}")
            return "", None

        if self.recognizer == "whisper":
            result, lang = self.recognize_whisper(wav_file)
            return result, lang

        if self.recognizer == "faster-whisper":
            result, lang = self.recognize_fast_whisper(wav_file)
            return result, lang
        return "", None

    def recognize_audio_data(self, audio_data: bytes):
        wav_file = audio_data_to_file(audio_data)
        try:
            result = self.recognize(wav_file)
            os.remove(wav_file)
        except Exception as e:
            print(e)
            result = "", None

        return result

    def recognize_whisper(self, wav_file):
        print("recognize_whisper" + wav_file)
        #  開始時刻
        start_time = time.time()

        # 言語オプション
        options = {}
        if self.config.whisper_target_lang is not None:
            options["language"] = self.config.whisper_target_lang

        result = self.model.transcribe(wav_file, **options)
        text = result["text"]
        lang = result["language"]

        # 暫定の対策
        if text == "ありがとうございました":
            text = ""
        if text == "はい":
            text = ""

        # 経過時間
        lapse_time = time.time() - start_time
        print(f"whisper({lang}):({lapse_time:.2f}秒) : {text}")
        return text, lang

    def recognize_fast_whisper(self, wav_file):

        #  開始時刻
        start_time = time.time()

        if self.config.faster_whisper_model is None:
            segments, info = self.model.transcribe(wav_file, beam_size=5)
        else:
            segments, info = self.model.transcribe(wav_file, beam_size=5, language=self.config.faster_whisper_target_language)

        text = ""
        for segment in segments:
            text += segment.text
            # print(f"[%.2fs -> %.2fs] %s {text}" % (segment.start, segment.end, segment.text))

        # 最初の空白をトリム
        text = text.strip()

        # よくまちがえるyouは無視
        if text == "You":
            text = ""
        if text == "you":
            text = ""
        # "MBC뉴스"がふくまれていたら無効
        if "MBC뉴스" in text:
            text = ""
        if "MBC 뉴스" in text:
            text = ""
        if text == "ありがとうございました":
            text = ""
        if "ご視聴ありがとうございました" in text:
            text = ""

        if info.language == "nn":
            text = ""

        # 同じ内容の文字が繰り返される場合は無視
        if len(text) > 0:
            if text[0] == text[-1]:
                text = ""

        lang = info.language
        # 経過時間
        lapse_time = time.time() - start_time
        print(f"whisper({lang}):({lapse_time:.2f}秒) : {text}")

        return text, info.language
