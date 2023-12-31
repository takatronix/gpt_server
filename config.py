class Config:
    # サーバー設定
    host = "localhost"
    port = 9090  # サーバーのポート
    use_ssl = False  # SSLを使用するかどうか

    # credentials
    ssl_certfile = "cert.pem"
    ssl_keyfile = "privkey.pem"
    openai_api_key = "openai_api_key"


    # その他の設定
    device = "cuda"  # 使用するデバイス
    #ai_key = "test"  # 使用するAIの種類
    ai_key = "translator"  # 使用するAIの種類
    voice_synthesizer = "openai"

    # 音声認識器の設定
    recognizer = "faster-whisper"
    # whisperのモデル
    whisper_model = "large-v3"
    whisper_target_lang = "ja-JP"
    # faster-whisperのモデル
    faster_whisper_model = "flyingleafe/faster-whisper-large-v3"
    faster_whisper_target_language = ""

