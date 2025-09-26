document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam-video');
    const emotionText = document.getElementById('emotion-text');
    const playlistTitle = document.getElementById('playlist-title');
    const playlistDesc = document.getElementById('playlist-desc');
    const songList = document.getElementById('song-list');
    const spinner = document.getElementById('spinner');

    const cameraModeBtn = document.getElementById('camera-mode-btn');
    const textModeBtn = document.getElementById('text-mode-btn');
    const cameraView = document.getElementById('camera-view');
    const textView = document.getElementById('text-view');
    const searchBtn = document.getElementById('search-btn');
    const moodInput = document.getElementById('mood-input');

    const themeBtn = document.getElementById('theme-btn');
    let isCameraActive = true;
    let detectionInterval;

    // Toggle between camera and text modes
    cameraModeBtn.addEventListener('click', () => {
        if (!isCameraActive) {
            cameraModeBtn.classList.add('active');
            textModeBtn.classList.remove('active');
            cameraView.classList.add('active-mode');
            textView.classList.remove('active-mode');
            isCameraActive = true;
            startCameraAndDetection();
        }
    });

    textModeBtn.addEventListener('click', () => {
        if (isCameraActive) {
            textModeBtn.classList.add('active');
            cameraModeBtn.classList.remove('active');
            textView.classList.add('active-mode');
            cameraView.classList.remove('active-mode');
            isCameraActive = false;
            stopCameraAndDetection();
        }
    });

    // Handle text-based search
    searchBtn.addEventListener('click', () => {
        const mood = moodInput.value;
        if (mood) {
            detectEmotionFromText(mood);
        }
    });

    // Theme toggle
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        themeBtn.textContent = isDarkMode ? '🌙' : '☀️';
    });

    // Function to start the camera and polling loop
    const startCameraAndDetection = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
            // Clear any existing interval
            if (detectionInterval) clearInterval(detectionInterval);
            detectionInterval = setInterval(detectEmotionFromVideo, 2000); // Poll every 2 seconds
        } catch (err) {
            console.error("Error accessing webcam: ", err);
        }
    };

    // Function to stop the camera and polling loop
    const stopCameraAndDetection = () => {
        if (video.srcObject) {
            const tracks = video.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
        if (detectionInterval) {
            clearInterval(detectionInterval);
        }
    };

    // Main loop for emotion detection from video
    const detectEmotionFromVideo = () => {
        if (!isCameraActive || video.readyState !== 4) return; // Ensure video is ready

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageDataUrl = canvas.toDataURL('image/jpeg');
        spinner.style.display = 'block';

        fetch('/api/detect_emotion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageDataUrl })
        })
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            if (data.success) {
                emotionText.textContent = data.emotion;
                updatePlaylist(data.playlist);
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error:', error);
        });
    };

    // Function for text-based emotion detection
    const detectEmotionFromText = (text) => {
        spinner.style.display = 'block';
        fetch('/api/search_mood', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood: text })
        })
        .then(response => response.json())
        .then(data => {
            spinner.style.display = 'none';
            if (data.success) {
                emotionText.textContent = data.emotion;
                updatePlaylist(data.playlist);
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            console.error('Error:', error);
        });
    };

    // Function to update the UI with the new playlist
    const updatePlaylist = (playlist) => {
        playlistTitle.textContent = playlist.title;
        playlistDesc.textContent = playlist.description;
        songList.innerHTML = '';
        playlist.songs.forEach(song => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="song-info">
                    <span class="song-title">${song.title}</span> by <span class="song-artist">${song.artist}</span>
                </div>
                <a href="${song.url}" target="_blank" class="play-btn">▶️ Play</a>
            `;
            songList.appendChild(li);
        });
    };

    // Start the camera and the main detection loop on page load
    startCameraAndDetection();
});