// =========================================================
// 🎧 Pemutar Musik MP3 - BAGUS MEDIA SERVER
// =========================================================

const audio = document.getElementById('audio-player');
const playBtn = document.getElementById('play-btn');
const pauseBtn = document.getElementById('pause-btn');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const shuffleBtn = document.getElementById('shuffle-btn');
const repeatBtn = document.getElementById('repeat-btn');
const volumeSlider = document.getElementById('volume-slider');
const progress = document.getElementById('progress');
const nowPlaying = document.getElementById('now-playing-title');
const playlistItems = document.querySelectorAll('.playlist-item');
const visualizer = document.querySelector('.visualizer');
const shuffleStatus = document.getElementById('shuffle-status');
const repeatStatus = document.getElementById('repeat-status');

let currentIndex = 0;
let isShuffle = false;
let isRepeat = false;

// 🎵 Daftar lagu dari playlist
const tracks = Array.from(playlistItems).map(item => item.dataset.src);

// Fungsi memutar lagu
function playTrack(index) {
    if (index < 0 || index >= tracks.length) return;
    currentIndex = index;
    audio.src = tracks[currentIndex];
    audio.play();
    updateNowPlaying();
    visualizer.classList.add('active');
}

// Update judul lagu
function updateNowPlaying() {
    const trackName = playlistItems[currentIndex].querySelector('.track-name').textContent;
    nowPlaying.textContent = `🎧 Sedang diputar: ${trackName}`;
}

// Tombol Play / Pause
playBtn.onclick = () => {
    if (audio.src === '') playTrack(0);
    else audio.play();
    visualizer.classList.add('active');
};

pauseBtn.onclick = () => {
    audio.pause();
    visualizer.classList.remove('active');
};

// Tombol Next / Prev
nextBtn.onclick = () => {
    if (isShuffle) currentIndex = Math.floor(Math.random() * tracks.length);
    else currentIndex = (currentIndex + 1) % tracks.length;
    playTrack(currentIndex);
};

prevBtn.onclick = () => {
    currentIndex = (currentIndex - 1 + tracks.length) % tracks.length;
    playTrack(currentIndex);
};

// Shuffle & Repeat
shuffleBtn.onclick = () => {
    isShuffle = !isShuffle;
    shuffleStatus.textContent = `Shuffle: ${isShuffle ? 'On' : 'Off'}`;
    shuffleStatus.style.color = isShuffle ? '#0ff' : '#aaa';
};

repeatBtn.onclick = () => {
    isRepeat = !isRepeat;
    repeatStatus.textContent = `Repeat: ${isRepeat ? 'On' : 'Off'}`;
    repeatStatus.style.color = isRepeat ? '#ff00ff' : '#aaa';
};

// Volume
volumeSlider.oninput = () => {
    audio.volume = volumeSlider.value / 100;
};

// Progress bar update
audio.addEventListener('timeupdate', () => {
    const percent = (audio.currentTime / audio.duration) * 100;
    progress.style.width = percent + '%';
});

// Klik pada playlist
playlistItems.forEach((item, index) => {
    item.querySelector('.play-track').addEventListener('click', () => playTrack(index));
});

// Jika lagu selesai
audio.addEventListener('ended', () => {
    if (isRepeat) playTrack(currentIndex);
    else nextBtn.click();
});

// 🌙 Tema Toggle
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light');
    if (document.body.classList.contains('light')) {
        document.body.style.background = "radial-gradient(circle at center, #f0f0ff 0%, #cce0ff 100%)";
        themeToggle.textContent = "☀️";
    } else {
        document.body.style.background = "radial-gradient(circle at center, #000010 0%, #020111 100%)";
        themeToggle.textContent = "🌙";
    }
});

function playSong(filename) {
    const audio = document.getElementById("audio-player");
    const source = document.getElementById("audio-source");
    const current = document.getElementById("current-song");

    source.src = `/media/mp3/${filename}`;
    audio.load();
    audio.play();

    current.textContent = filename;
}