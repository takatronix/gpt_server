MEDIA_TYPE_JSON = 0x00
MEDIA_TYPE_AUDIO = 0x01
MEDIA_TYPE_IMAGE = 0x02

// config.jsonから設定を読み込む
let url = '';
let useSSL = true;
fetch('config.json')
    .then(response => response.json())
    .then(config => {
        useSSL = config.useSSL;
        if(useSSL){
            url = "wss://" + config.url;
        }else{
            url = "ws://" + config.url;
        }
        setupWebSocket();
    })
    .catch(error => console.error('Error loading config:', error));


var averageVolume = 0;
var isMicOn = false;
var isSpeakerOn= false;
var isChatOn = false;
var isBurgerOn = false;


let mediaRecorder;
let audioChunks = [];
let socket;
let mediaStream; // グローバルスコープに追加

// 録音を開始するボリュームレベル
var startThreshold = 20; // 録音を開始するボリュームレベル
var stopThreshold = 35; //　録音を停止するボリュームレベル
let silenceTime = 200; // 静けさが続くべきミリ秒数
let recording = false;
let stopStartTime = null;
let recordStartTime = null;
// 最低録音時間
const MIN_RECORDING_TIME = 2500;

var audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function startRecording() {
    // 切断してたら再接続
    if(socket.readyState !== WebSocket.OPEN){
        setupWebSocket();
    }
    if (mediaStream) {
        // 既に mediaStream がある場合、新たに getUserMedia を呼び出さずに録音を開始
        initializeMediaRecorder(mediaStream);
    } else {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaStream = stream; // mediaStream を保存
                initializeMediaRecorder(stream);
            })
            .catch(error => {
                error_message("Error accessing the microphone: " + error);
            });
    }
}
function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
    }
}

function error_message(message){
    addMessage(message,"error_message");
    console.log(message);
}


function setupWebSocket() {

    message("Connecting to server: " + url)
    socket = new WebSocket(url);
    socket.binaryType = 'blob'; // または 'arraybuffer'
    socket.onopen = function(event) {
        message("WebSocket is open now.");
    };

    //  メッセージ受信
    socket.onmessage =  function (event) {
        console.log("Message from server:" + event.data);

           var audioData = event.data;
/*
        const arrayBuffer =  event.data.arrayBuffer();
        const dataView = new DataView(arrayBuffer);

        // 先頭の1バイトを読み取る
        const mediaType = dataView.getUint8(0);
        // dataに先頭の1バイトを除いた残りのデータを格納

 */
        const data = audioData.slice(1);

        if (event.data instanceof Blob) {
                // AudioContextを使用してオーディオデータをデコード
                audioCtx.decodeAudioData(audioData, function (buffer) {
                    // AudioBufferSourceNodeの作成
                    var source = audioCtx.createBufferSource();
                    source.buffer = buffer;
                    source.connect(audioCtx.destination);
                    source.start(0);
                }, function (e) {
                    console.log("Error with decoding audio data" + e.err);
                });

                return;
        }
        /*
        // event.dataがBlobオブジェクトであることを確認
        if (event.data instanceof Blob) {


            try {
                // BlobをArrayBufferに変換
                const arrayBuffer =  event.data.arrayBuffer();
                const dataView = new DataView(arrayBuffer);

                // 先頭の1バイトを読み取る
                const mediaType = dataView.getUint8(0);
                // dataに先頭の1バイトを除いた残りのデータを格納
                const data = arrayBuffer.slice(1);

                console.log("Media type:", mediaType);


                if (mediaType === MEDIA_TYPE_AUDIO && isSpeakerOn){


                    audioCtx.decodeAudioData(data, function (buffer) {
                        var source = audioCtx.createBufferSource();
                        source.buffer = buffer;
                        source.connect(audioCtx.destination);
                        source.start(0);
                    }, function (e) {
                        console.error("Error with decoding audio data: " + e.err);
                    });
                }
            } catch (error) {
                message("Error: " + error)
            }
            return;
        }
*/

        addMessage(event.data, 'result-bubble');
    };

    socket.onclose = function(event) {
        message("WebSocket is closed now.");
    };

    socket.onerror = function(event) {
        error_message("WebSocket error observed.");
    };
}

function sendData(data) {

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(data);
    } else {
        console.error("WebSocket is not open. Data not sent.");
    }

}

let audioContext, analyser, microphone, javascriptNode;

function updateVolume(stream) {
    audioContext = new AudioContext();
    analyser = audioContext.createAnalyser();
    microphone = audioContext.createMediaStreamSource(stream);
    javascriptNode = audioContext.createScriptProcessor(2048, 1, 1);

    analyser.smoothingTimeConstant = 0.8;
    analyser.fftSize = 1024;

    microphone.connect(analyser);
    analyser.connect(javascriptNode);
    javascriptNode.connect(audioContext.destination);
    javascriptNode.onaudioprocess = function() {
        const array = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(array);
        let values = 0;
        const length = array.length;
        for (let i = 0; i < length; i++) {
            values += (array[i]);
        }
        averageVolume = values / length;

        let volumeLevel = document.getElementById('volume-level');
        volumeLevel.style.width = averageVolume + '%';
        checkVolumeLevel();
    }
}

// ボリュームレベルをチェックする関数
function checkVolumeLevel() {
    // ボリュームレベルを取得
    let volumeLevel = averageVolume;

    // ボリュームレベルに応じてステータスを設定
    let status = '';
    // ボリュームレベルを表示


    // ボリュームが閾値を下回っているかチェック
    if (volumeLevel < stopThreshold) {
        status += "↓"
        // 初めて静けさが検出されたら、タイマーを開始
        if (!stopStartTime) {
            stopStartTime = Date.now();
        }

        // 一定時間静けさが続いているかチェック
        var laps = Date.now() - stopStartTime;
        if (laps > silenceTime) {
            //log_message("Silence detected.")
            if (recording) {

                // recordStartTimeからの経過時間を取得
                const recordTime = Date.now() - recordStartTime;
                // 最低録音時間より短い場合は録音を破棄
                if (recordTime < MIN_RECORDING_TIME) {
                    return;
                }
                // 録音を停止し、データをサーバーに送信
                stopRecording();
                recording = false;
            }
        }else{
            if(laps > 0)
            status = status + "silenceTime:" + laps + "ms";
        }
    }else{
        // 静けさのタイマーをリセット
        stopStartTime = null;
    }

    if(volumeLevel > startThreshold)
    {

        status += "↑"
        // ボリュームが閾値を超えている場合
        if (!recording) {
            // 録音を開始
            startRecording();
            recording = true;
            recordStartTime = Date.now();
        }
    }

    setStatusText(status);
}

function setSliderValue(value) {
    document.getElementById('recording-level-slider').value = value;
    document.getElementById('recording-level-value').textContent = value;
    startThreshold = value;
}
function setStatusText(text) {
    document.getElementById('status-text').textContent = text;
}

// 静寂時間の値を取得して設定する
function loadSilenceTime() {
    // ローカルストレージから値を取得する
    const savedSilenceTime = localStorage.getItem('silenceTime');
    if (savedSilenceTime) {
        silenceTime = parseInt(savedSilenceTime, 10);
        document.getElementById('silence-time-input').value = silenceTime;
    }
}
function loadSilenceThreshold(){
    // ローカルストレージから値を取得する
    const savedSilenceThreshold = localStorage.getItem('silenceThreshold');
    if (savedSilenceThreshold) {
        startThreshold = parseInt(savedSilenceThreshold, 10);
        setSliderValue(startThreshold);
    }
}

/*
// 保存ボタンがクリックされたときに静寂時間を保存する
document.getElementById('save-silence-time').addEventListener('click', function() {
    const inputVal = document.getElementById('silence-time-input').value;
    silenceTime = parseInt(inputVal, 10);
    // ローカルストレージに値を保存する
    localStorage.setItem('silenceTime', silenceTime);
    log_message('静寂時間が保存されました: ' + silenceTime + 'ミリ秒');

    // silenceThresholdの保存
    const inputVal2 = document.getElementById('recording-level-slider').value;
    startThreshold = parseInt(inputVal2, 10);
    // ローカルストレージに値を保存する
    localStorage.setItem('silenceThreshold', startThreshold);
    log_message('静寂閾値が保存されました: ' + startThreshold);

});
*/

function clear_messages(){
    document.getElementById('messages').innerHTML = '';
}


// Save messages to a text file
function save_messages(){
    var htmlContent = document.getElementById('messages').innerHTML;
    // HTMLのブロック要素を改行に置換
    var textContent = htmlContent.replace(/<\/div>|<\/p>|<br>/gi, '\n').replace(/<[^>]+>/g, '');
    var blob = new Blob([textContent], {type: 'text/plain'});
    var anchor = document.createElement('a');
    anchor.download = 'messages.txt';
    anchor.href = window.URL.createObjectURL(blob);
    anchor.click();
    window.URL.revokeObjectURL(anchor.href);
}


function initializeMediaRecorder(stream) {
    updateVolume(stream);

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };
    mediaRecorder.onstop = () => {
        let audioBlob = new Blob(audioChunks, { type: 'audio/wav' });


    // audioBlobからArrayBufferを取得
    audioBlob.arrayBuffer().then(arrayBuffer => {
        // 1バイトの0x02を追加するためのUint8Arrayを作成
        let audioDataWithHeader = new Uint8Array(arrayBuffer.byteLength + 1);
        audioDataWithHeader[0] = MEDIA_TYPE_AUDIO; // 1バイト目に0x01を追加(音声)

        // 残りの部分にaudioBlobのデータをコピー
        audioDataWithHeader.set(new Uint8Array(arrayBuffer), 1);

        // 新しいBlobを作成
        let newAudioBlob = new Blob([audioDataWithHeader], { type: 'audio/wav' });

        // データの送信
        if(isMicOn){
            sendData(newAudioBlob);
        }
    });
        audioChunks = [];
        on_stop_recording();
    };
    mediaRecorder.start();
    on_start_recording();
}


// DOMが完全に読み込まれた後に実行する関数
document.addEventListener('DOMContentLoaded', (event) => {

    document.getElementById('mic-button').addEventListener('click', on_mic_button_click);
    document.getElementById('speaker-button').addEventListener('click', on_speaker_button_click);
    document.getElementById('chat-button').addEventListener('click', on_chat_button_click);
    document.getElementById('burger-button').addEventListener('click', on_burger_button_click);
    document.getElementById('upload-button').addEventListener('click', on_enter_message);

    // テキスト入力フィールドの要素を取得
    // テキスト入力フィールドのキーダウンイベントリスナーを追加（エンターキーを押したときの処理）
    document.getElementById('messageInput').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            on_enter_message();
        }
    });

    // マイクは最初はオフ
    isMicOn = false
    set_mic_ui(false);
    let volumeLevel = document.getElementById('volume-level');
    volumeLevel.style.backgroundColor = 'black';

    set_speaker(false);
});

function on_enter_message(){
    let messageInput = document.getElementById('messageInput');
    let text = messageInput.value; // 入力されたテキストを取得
    messageInput.value = ''; // テキストフィールドをクリア

    // テキストが空の場合は何もしない
    if (!text) {
        return;
    }

    // 切断してたら再接続
    if(socket.readyState !== WebSocket.OPEN){
        setupWebSocket();
    }

    bubble_message(text);
    sendData(text);
}


function on_mic_button_click() {
    if(isMicOn){
        set_mic_ui(false);
        stopRecording();
        isMicOn = false;
    }
    else{
        set_mic_ui(true);
        startRecording();
        isMicOn = true;
    }
}
function on_speaker_button_click() {
    const speakerButton = document.getElementById('speaker-button');
    if(isSpeakerOn){
        set_speaker(false);
    }
    else{
        set_speaker(true);
    }
}
function on_start_recording() {
   // message('Recording started.')
}
function on_stop_recording() {
   /// message('Recording stopped.')
}
function on_chat_button_click() {
    if(isChatOn)
        set_chat(false);
    else
       set_chat(true);
}
function on_burger_button_click() {
    var burgerButton = document.getElementById('burger-button');
    if(isBurgerOn)
        set_burger(false);
    else
        set_burger(true);

}
function set_mic_ui(isOn) {
    let micButton = document.getElementById('mic-button');
    let volumeLevel = document.getElementById('volume-level');
    if(isOn){
        micButton.style.opacity = '1.0';
        volumeLevel.style.backgroundColor = 'red';
        volumeLevel.style.opacity = '1.0';
    }
    else{
        micButton.style.opacity = '0.5';
        volumeLevel.style.backgroundColor = 'green';
        volumeLevel.style.opacity = '0.5';
    }

    isMicOn = isOn;
}
function set_speaker(isOn) {
    let speakerButton = document.getElementById('speaker-button');
    if(isOn){
        speakerButton.style.opacity = '1.0';
    }
    else{
        speakerButton.style.opacity = '0.5';
    }
    isSpeakerOn = isOn;
}
function set_burger(isOn) {
    let burgerButton = document.getElementById('burger-button');
    let setting = document.getElementById('setting');
    if(isOn){
        burgerButton.style.opacity = '1.0';
        setting.style.visibility = 'hidden';
    }
    else{
        burgerButton.style.opacity = '0.5';
        setting.style.visibility = 'visible';
    }
    isBurgerOn = isOn;

}
function set_chat(isOn) {
    let messageArea = document.getElementById('footer');
    let chatArea = document.getElementById('chat');
    let chatButton = document.getElementById('chat-button');

    if(isOn){
        messageArea.style.display = 'block';
        chatArea.style.bottom = '50px';
        chatButton.style.opacity = '1.0';
    }
    else{
        messageArea.style.display = 'none';
        chatArea.style.bottom = '0px';
        chatButton.style.opacity = '0.5';
    }
    isChatOn = isOn;
}




function message(message){
    console.log(message);
    addMessage(message);
}
function bubble_message(message){
    console.log(message);
    addMessage(message,'speech-bubble');
}


function addMessage(message,className) {
    console.log(message);
    let chatContainer = document.querySelector('.chat');

    const balloon = document.createElement('div');
    balloon.classList.add(className);
    balloon.textContent = message;
    // 自動スクロール
    chatContainer.appendChild(balloon);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}