const audioPlayer = document.getElementById('audio-player');
const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const repeatBtn = document.getElementById('repeat-btn');
const progress = document.getElementById('progress');
const currentTimeEl = document.getElementById('current-time');
const durationEl = document.getElementById('duration');
const volumeSlider = document.getElementById('volume-slider');
const nowPlayingTitle = document.getElementById('now-playing-title');
const playlistItems = document.querySelectorAll('.playlist-item');
const visualizerBars = document.querySelectorAll('.visualizer div');

let currentTrackIndex = 0;
let isShuffle = false;
let repeatMode = "off"; // off | one | all
const tracks = Array.from(playlistItems);

// ------------------- FUNGSI DASAR -------------------
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

    audioPlayer.src = trackSrc;
    nowPlayingTitle.textContent = "🎧 " + trackName;

    progress.style.width = '0%';
    currentTimeEl.textContent = '0:00';

    tracks.forEach(item => item.classList.remove('active'));
    track.classList.add('active');

    audioPlayer.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(audioPlayer.duration);
    }, { once: true });

    pauseTrack(); // tidak autoplay
}

function playTrack() {
    audioPlayer.play();
    playBtn.style.display = 'none';
    pauseBtn.style.display = 'inline-block';
    visualizerBars.forEach(bar => bar.style.animationPlayState = 'running');
}

function pauseTrack() {
    audioPlayer.pause();
    playBtn.style.display = 'inline-block';
    pauseBtn.style.display = 'none';
    visualizerBars.forEach(bar => bar.style.animationPlayState = 'paused');
}

// ------------------- NAVIGASI LAGU -------------------
function nextTrack() {
    if (isShuffle) {
        currentTrackIndex = Math.floor(Math.random() * tracks.length);
    } else {
        currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
    }
    loadTrack(currentTrackIndex);
    playTrack();
}

function prevTrack() {
    currentTrackIndex = (currentTrackIndex - 1 + tracks.length) % tracks.length;
    loadTrack(currentTrackIndex);
    playTrack();
}

// ------------------- EVENT KONTROL -------------------
playBtn.addEventListener('click', playTrack);
pauseBtn.addEventListener('click', pauseTrack);
nextBtn.addEventListener('click', nextTrack);
prevBtn.addEventListener('click', prevTrack);

volumeSlider.addEventListener('input', function() {
    audioPlayer.volume = this.value / 100;
});

shuffleBtn.addEventListener('click', () => {
    isShuffle = !isShuffle;
    shuffleBtn.style.background = isShuffle ? '#00aaff' : '#00e1ff';
});

// Ganti mode repeat
repeatBtn.addEventListener('click', () => {
    if (repeatMode === "off") {
        repeatMode = "one";
        repeatBtn.textContent = "🔂"; // repeat satu lagu
        repeatBtn.style.background = "#00aaff";
    } else if (repeatMode === "one") {
        repeatMode = "all";
        repeatBtn.textContent = "🔁";
        repeatBtn.style.background = "#0088ff";
    } else {
        repeatMode = "off";
        repeatBtn.textContent = "🔁";
        repeatBtn.style.background = "#00e1ff";
    }
});

// ------------------- UPDATE WAKTU & PROGRESS -------------------
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

// ------------------- SAAT LAGU SELESAI -------------------
audioPlayer.addEventListener('ended', function() {
    if (repeatMode === "one") {
        playTrack(); // ulang lagu yang sama
    } else if (repeatMode === "all") {
        if (currentTrackIndex === tracks.length - 1) {
            loadTrack(0); // mulai dari awal lagi
        } else {
            nextTrack();
        }
        playTrack();
    } else {
        nextTrack(); // mode normal
    }
});

// ------------------- PLAYLIST -------------------
playlistItems.forEach((item, index) => {
    item.querySelector('.play-track').addEventListener('click', function() {
        loadTrack(index);
        playTrack();
    });
});

// ------------------- AWAL -------------------
if (tracks.length > 0) {
    loadTrack(0);
}