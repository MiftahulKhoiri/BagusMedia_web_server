// ==========================
// 🎧 PEMUTAR MP3 DENGAN PARTIKEL NEON REAKTIF
// ==========================

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

let currentTrackIndex = 0;
let isShuffle = false;
let repeatMode = "off";
const tracks = Array.from(playlistItems);

// ==========================
// 🔊 FUNGSI PEMUTARAN DASAR
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

    audioPlayer.src = trackSrc;
    nowPlayingTitle.textContent = "🎧 " + trackName;

    progress.style.width = '0%';
    currentTimeEl.textContent = '0:00';
    durationEl.textContent = '0:00';

    tracks.forEach(item => item.classList.remove('active'));
    track.classList.add('active');

    audioPlayer.addEventListener('loadedmetadata', () => {
        durationEl.textContent = formatTime(audioPlayer.duration);
    }, { once: true });

    pauseTrack();
}

function playTrack() {
    audioPlayer.play().catch(err => {
        console.warn("Autoplay diblokir browser. Silakan klik tombol play.");
    });
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

// ==========================
// 🎛️ EVENT KONTROL
// ==========================
playBtn.addEventListener('click', () => {
    playTrack();
    initAudioAnalyser(); // Inisialisasi audio analyser saat user klik play
});

pauseBtn.addEventListener('click', pauseTrack);
nextBtn.addEventListener('click', nextTrack);
prevBtn.addEventListener('click', prevTrack);

volumeSlider.addEventListener('input', function() {
    audioPlayer.volume = this.value / 100;
});

shuffleBtn.addEventListener('click', () => {
    isShuffle = !isShuffle;
    shuffleStatus.textContent = `Shuffle: ${isShuffle ? 'On' : 'Off'}`;
    shuffleStatus.style.color = isShuffle ? '#00ffff' : '#ccc';
});

repeatBtn.addEventListener('click', () => {
    if (repeatMode === "off") {
        repeatMode = "one";
        repeatStatus.textContent = "Repeat: One";
        repeatStatus.style.color = "#00ffff";
    } else if (repeatMode === "one") {
        repeatMode = "all";
        repeatStatus.textContent = "Repeat: All";
        repeatStatus.style.color = "#00ffff";
    } else {
        repeatMode = "off";
        repeatStatus.textContent = "Repeat: Off";
        repeatStatus.style.color = "#ccc";
    }
});

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

audioPlayer.addEventListener('ended', function() {
    if (repeatMode === "one") {
        playTrack();
    } else if (repeatMode === "all") {
        currentTrackIndex = (currentTrackIndex + 1) % tracks.length;
        loadTrack(currentTrackIndex);
        playTrack();
    } else {
        nextTrack();
    }
});

tracks.forEach((item, index) => {
    item.querySelector('.play-track').addEventListener('click', function() {
        loadTrack(index);
        playTrack();
        initAudioAnalyser(); // Pastikan visualizer aktif saat klik track
    });
});

if (tracks.length > 0) loadTrack(0);

// ==========================
// 🌙 MODE MALAM OTOMATIS
// ==========================
const themeToggle = document.getElementById('theme-toggle');
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
// 🌈 PARTIKEL NEON REAKTIF
// ==========================
const canvas = document.getElementById('neon-particles');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
const numParticles = 120;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.3;
        this.speedY = (Math.random() - 0.5) * 0.3;
        this.color = "rgba(0,255,255,0.3)";
    }

    update(energy) {
        this.x += this.speedX * (1 + energy / 150);
        this.y += this.speedY * (1 + energy / 150);
        if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.fill();
    }
}

for (let i = 0; i < numParticles; i++) {
    particles.push(new Particle());
}

let audioCtx, analyser, dataArray;

function initAudioAnalyser() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaElementSource(audioPlayer);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);
        source.connect(analyser);
        analyser.connect(audioCtx.destination);
    }
}

function animateParticles() {
    requestAnimationFrame(animateParticles);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    let energy = 0;
    if (analyser) {
        analyser.getByteFrequencyData(dataArray);
        energy = dataArray.slice(0, 40).reduce((a, b) => a + b, 0) / 40;
    }

    const hue = 180 + energy / 5;
    particles.forEach(p => {
        p.color = `hsla(${hue}, 100%, 60%, ${0.2 + energy / 300})`;
        p.update(energy);
        p.draw();
    });
}

animateParticles();

window.addEventListener('resize', () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
});