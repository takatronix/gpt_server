import time

import whisper
from faster_whisper import WhisperModel


class SpeechRecognizer:
    def __init__(self, config, recognizer):
        self.target_language = config.translation_target_lang
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
            print("(faster-whisper) model loaded")

    def recognize(self, wav_file):
        if self.recognizer == "whisper":
            result, lang = self.recognize_whisper(wav_file)
            return result, lang

        if self.recognizer == "faster-whisper":
            result, lang = self.recognize_fast_whisper(wav_file)
            return result, lang
        return "", None

    def recognize_whisper(self, wav_file):
        print("recognize_whisper" + wav_file)
        #  開始時刻
        start_time = time.time()

        # 言語オプション
        options = {}
        if self.config.whisper_target_lang != "":
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

        segments, info = self.model.transcribe(wav_file, beam_size=5,language=self.config.faster_whisper_target_lang)

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
