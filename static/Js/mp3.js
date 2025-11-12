const audioPlayer = document.getElementById('audio-player');
const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const repeatBtn = document.getElementById('repeat-btn');
const shuffleStatus = document.getElementById('shuffle-status');
const repeatStatus = document.getElementById('repeat-status');
const progress = document.getElementById('progress');
const currentTimeEl = document.getElementById('current-time');
const durationEl = document.getElementById('duration');
const volumeSlider = document.getElementById('volume-slider');
const nowPlayingTitle = document.getElementById('now-playing-title');
const playlistItems = document.querySelectorAll('.playlist-item');
const visualizerBars = document.querySelectorAll('.visualizer div');
const themeToggle = document.getElementById('theme-toggle');

let currentTrackIndex = 0;
let isShuffle = false;
let repeatMode = "off"; // off | one | all
const tracks = Array.from(playlistItems);
let audioContext, analyser, dataArray, source;

// ==========================
// 🎵 FUNGSI DASAR
// ==========================
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function loadTrack(index) {
    if (tracks.length === 0) return;
    currentTrackIndex = index;
    const track = tracks[currentTrackIndex];
    const trackSrc = track.getAttribute('data-src');
    const trackName = track.querySelector('.track-name').textContent;

    // Fade-out sebelum ganti lagu
    fadeOutAudio(() => {
        audioPlayer.src = trackSrc;
        nowPlayingTitle.textContent = "🎧 " + trackName;
        progress.style.width = '0%';
        currentTimeEl.textContent = '0:00';
        tracks.forEach(item => item.classList.remove('active'));
        track.classList.add('active');

        audioPlayer.addEventListener('loadedmetadata', () => {
            durationEl.textContent = formatTime(audioPlayer.duration);
        }, { once: true });

        fadeInAudio();
        playTrack();
    });
}

// ==========================
// ▶️ KONTROL PLAYBACK
// ==========================
function playTrack() {
    audioPlayer.play();
    playBtn.style.display = 'none';
    pauseBtn.style.display = 'inline-block';
    initVisualizer();
    document.body.classList.add('glow-active');
}

function pauseTrack() {
    audioPlayer.pause();
    playBtn.style.display = 'inline-block';
    pauseBtn.style.display = 'none';
    document.body.classList.remove('glow-active');
}

// Fade in/out volume untuk transisi halus
function fadeOutAudio(callback) {
    const fadeInterval = setInterval(() => {
        if (audioPlayer.volume > 0.1) {
            audioPlayer.volume -= 0.1;
        } else {
            audioPlayer.volume = 0;
            clearInterval(fadeInterval);
            if (callback) callback();
        }
    }, 50);
}

function fadeInAudio() {
    audioPlayer.volume = 0;
    const fadeInterval = setInterval(() => {
        if (audioPlayer.volume < volumeSlider.value / 100) {
            audioPlayer.volume += 0.1;
        } else {
            clearInterval(fadeInterval);
        }
    }, 50);
}

// ==========================
// ⏩ NAVIGASI LAGU
// ==========================
function nextTrack() {
    if (isShuffle) {
        let nextIndex;
        do {
            nextIndex = Math.floor(Math.random() * tracks.length);
        } while (nextIndex === currentTrackIndex && tracks.length > 1);
        currentTrackIndex = nextIndex;
    } else {
        currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
    }
    loadTrack(currentTrackIndex);
}

function prevTrack() {
    currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
    loadTrack(currentTrackIndex);
}

// ==========================
// 🔊 EVENT HANDLER
// ==========================
playBtn.addEventListener('click', playTrack);
pauseBtn.addEventListener('click', pauseTrack);
nextBtn.addEventListener('click', nextTrack);
prevBtn.addEventListener('click', prevTrack);

// Volume kontrol
volumeSlider.addEventListener('input', function() {
    audioPlayer.volume = this.value / 100;
});

// Shuffle
shuffleBtn.addEventListener('click', () => {
    isShuffle = !isShuffle;
    shuffleBtn.style.background = isShuffle ? '#00aaff' : '#00e1ff';
    shuffleStatus.textContent = `Shuffle: ${isShuffle ? 'On' : 'Off'}`;
    shuffleStatus.style.color = isShuffle ? '#00aaff' : '#ccc';
});

// Repeat
repeatBtn.addEventListener('click', () => {
    if (repeatMode === "off") {
        repeatMode = "one";
        repeatBtn.textContent = "🔂";
        repeatStatus.textContent = "Repeat: One";
        repeatStatus.style.color = "#00aaff";
    } else if (repeatMode === "one") {
        repeatMode = "all";
        repeatBtn.textContent = "🔁";
        repeatStatus.textContent = "Repeat: All";
        repeatStatus.style.color = "#00d0ff";
    } else {
        repeatMode = "off";
        repeatBtn.textContent = "🔁";
        repeatStatus.textContent = "Repeat: Off";
        repeatStatus.style.color = "#ccc";
    }
});

// Progress bar
audioPlayer.addEventListener('timeupdate', function() {
    const currentTime = audioPlayer.currentTime;
    const duration = audioPlayer.duration;
    if (duration) {
        const progressPercent = (currentTime / duration) * 100;
        progress.style.width = `${progressPercent}%`;
        currentTimeEl.textContent = formatTime(currentTime);
    }
});

document.querySelector('.progress-bar').addEventListener('click', function(e) {
    const clickPosition = e.offsetX;
    const progressBarWidth = this.offsetWidth;
    const seekTime = (clickPosition / progressBarWidth) * audioPlayer.duration;
    audioPlayer.currentTime = seekTime;
});

// Lagu selesai
audioPlayer.addEventListener('ended', function() {
    if (repeatMode === "one") {
        playTrack();
    } else if (repeatMode === "all") {
        nextTrack();
    } else {
        nextTrack();
    }
});

// Playlist klik
playlistItems.forEach((item, index) => {
    item.querySelector('.play-track').addEventListener('click', function() {
        loadTrack(index);
    });
});

// ==========================
// 🌙 MODE GELAP OTOMATIS
// ==========================
const currentHour = new Date().getHours();
if (currentHour >= 18 || currentHour < 6) {
    document.body.classList.add('dark-mode');
    themeToggle.textContent = "☀️";
}
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    themeToggle.textContent = isDark ? "☀️" : "🌙";
});

// ==========================
// 💡 VISUALIZER AUDIO
// ==========================
function initVisualizer() {
    if (!audioContext) {
        audioContext = new AudioContext();
        source = audioContext.createMediaElementSource(audioPlayer);
        analyser = audioContext.createAnalyser();
        source.connect(analyser);
        analyser.connect(audioContext.destination);
        analyser.fftSize = 64;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        function renderFrame() {
            requestAnimationFrame(renderFrame);
            analyser.getByteFrequencyData(dataArray);
            visualizerBars.forEach((bar, i) => {
                const value = dataArray[i % bufferLength];
                const height = Math.max(2, value / 4);
                bar.style.height = `${height}px`;
            });
        }
        renderFrame();
    }
}

// ==========================
// ⏯ INIT AWAL
// ==========================
if (tracks.length > 0) {
    loadTrack(0);
}