import json


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            config_data = json.load(file)

        self.device = config_data.get('device')
        self.openai_api_key = config_data.get('openai_api_key')

        self.recognizer = config_data.get('recognizer')
        self.whisper_model = config_data.get('whisper_model')
        self.faster_whisper_model = config_data.get('faster_whisper_model')
        self.whisper_target_lang = config_data.get('whisper_target_lang')
        self.faster_whisper_target_lang = config_data.get('faster_whisper_target_lang')

        self.translator = config_data.get('translator')
        self.deepl_api_key = config_data.get('deepl_api_key')
        self.translation_target_lang = config_data.get('translation_target_lang')
        self.translation_source_lang = config_data.get('translation_source_lang')

        self.use_ssl = config_data.get('use_ssl')
        self.ssl_cert = config_data.get('ssl_cert')
        self.ssl_key = config_data.get('ssl_key')
        self.server_ip = config_data.get('server_ip')
        self.port_no = config_data.get('port_no')
        self.server_path = config_data.get('server_path')

    def __str__(self):
        return (f"Config(device='{self.device}', recognizer='{self.recognizer}', "
                f"whisper_model='{self.whisper_model}', faster_whisper_model='{self.faster_whisper_model}', "
                f"translator='{self.translator}', deepl_api_key='{self.deepl_api_key}', "
                f"translation_target_lang='{self.translation_target_lang}', translation_source_lang='{self.translation_source_lang}',"
                f"use_ssl={self.use_ssl}, ssl_cert='{self.ssl_cert}', ssl_key='{self.ssl_key}', "
                f"server_ip='{self.server_ip}', port_no={self.port_no}, server_path='{self.server_path}')")
