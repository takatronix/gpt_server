# gpt_server

whisper(or fast whisper)をつかって、高速に音声入力ができるchat gptサーバーと、ウェブクライアント　

## 実行方法
### サーバー
```python main.py```
### クライアント
```/client/index.html```をブラウザで開く

### スマートフォンなどで使う場合
webサーバー公開して音声入力を行うには、httpsでないといけないので、httpsで公開する必要があります。
また、WebSocket設定もSSLを有効にしてください。

#### クライアント設定
/client/config.json

```
{
  "url": "(server):9090/gpt",
  "useSSL": true
}
```

#### サーバー設定
config.json

SSLの設定を行ってください。
```
{
    "server_ip": "0.0.0.0",
    "port_no": 9090,
    "server_path": "/gpt",
    "use_ssl": true,
    "ssl_cert": "/path/to/cert.pem",
    "ssl_key": "/path/to/privkey.pem"
}
```