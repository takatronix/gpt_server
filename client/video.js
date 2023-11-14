document.addEventListener('DOMContentLoaded', () => {
    const videoContainer = document.getElementById('videoContainer');
    const video = document.getElementById('video');
    const toggleButton = document.getElementById('toggle');
    const switchCameraButton = document.getElementById('switchCamera');
    const resizeHandle = document.getElementById('resizeHandle');
    let isVideoVisible = true;
    let useFrontCamera = true;
    let currentStream;

    function stopCurrentStream() {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
    }

    // カメラを切り替える関数
    function switchCamera() {
        stopCurrentStream(); // 現在のストリームを停止
        useFrontCamera = !useFrontCamera;
        const constraints = {
            video: { facingMode: (useFrontCamera ? "user" : "environment") }
        };

        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {
                currentStream = stream;
                video.srcObject = stream;
            })
            .catch(error => {
                console.error('Error accessing the camera', error);
            });
    }

    // ビデオコンテナのドラッグアンドドロップ
    videoContainer.addEventListener('mousedown', function(event) {
        // コントロールまたはリサイズハンドル上でのドラッグを無視
        if (event.target.closest('#videoControls') || event.target.closest('#resizeHandle')) {
            return;
        }

        let startX = event.clientX;
        let startY = event.clientY;
        let origX = videoContainer.offsetLeft;
        let origY = videoContainer.offsetTop;
        let deltaX = startX - origX;
        let deltaY = startY - origY;

        function onMouseMove(event) {
            videoContainer.style.left = (event.clientX - deltaX) + 'px';
            videoContainer.style.top = (event.clientY - deltaY) + 'px';
        }

        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        event.preventDefault(); // ドラッグによるテキスト選択などを防ぐ
    });

    // ビデオの拡大縮小
    resizeHandle.addEventListener('mousedown', function(event) {
        let startX = event.clientX;
        let startY = event.clientY;
        let startWidth = videoContainer.clientWidth;
        let startHeight = videoContainer.clientHeight;

        function onMouseMove(event) {
            let newWidth = startWidth + event.clientX - startX;
            let newHeight = startHeight + event.clientY - startY;
            videoContainer.style.width = newWidth + 'px';
            videoContainer.style.height = newHeight + 'px';
        }

        function onMouseUp() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);

        event.preventDefault(); // ドラッグによるテキスト選択などを防ぐ
    });

    // ビデオの表示/非表示の切り替え
    toggleButton.addEventListener('click', () => {
        isVideoVisible = !isVideoVisible;
        video.style.display = isVideoVisible ? 'block' : 'none';
    });

    // カメラ切り替えボタンのイベントリスナー
    switchCameraButton.addEventListener('click', switchCamera);

    // 最初のカメラアクセス
    switchCamera();
});
