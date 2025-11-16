const videoPlayer = document.getElementById('video-player');
const videoPlayBtn = document.getElementById('video-play-btn');
const videoPauseBtn = document.getElementById('video-pause-btn');
const videoPrevBtn = document.getElementById('video-prev-btn');
const videoNextBtn = document.getElementById('video-next-btn');
const videoFullscreenBtn = document.getElementById('video-fullscreen-btn');
const videoShuffleBtn = document.getElementById('video-shuffle-btn');
const videoRepeatBtn = document.getElementById('video-repeat-btn');
const videoProgress = document.getElementById('video-progress');
const videoCurrentTimeEl = document.getElementById('video-current-time');
const videoDurationEl = document.getElementById('video-duration');
const videoVolumeSlider = document.getElementById('video-volume-slider');
const nowPlayingTitle = document.getElementById('now-playing-title');
const playlistItems = document.querySelectorAll('.playlist-item');

let currentVideoIndex = 0;
let isShuffle = false;
let isRepeat = false;
const videos = Array.from(playlistItems);

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function loadVideo(index, autoplay = false) {
    if (videos.length === 0) return;
    currentVideoIndex = index;
    const video = videos[currentVideoIndex];
    const videoSrc = video.getAttribute('data-src');
    const videoName = video.querySelector('.video-name').textContent;

    videoPlayer.src = videoSrc;
    nowPlayingTitle.textContent = videoName;
    videoProgress.style.width = '0%';
    videoCurrentTimeEl.textContent = '0:00';

    videos.forEach(item => item.classList.remove('active'));
    video.classList.add('active');

    videoPlayer.addEventListener('loadedmetadata', () => {
        videoDurationEl.textContent = formatTime(videoPlayer.duration);
    }, { once: true });

    if (autoplay) playVideo();
    else pauseVideo();
}

function playVideo() {
    videoPlayer.play();
    videoPlayBtn.style.display = 'none';
    videoPauseBtn.style.display = 'inline-block';
}

function pauseVideo() {
    videoPlayer.pause();
    videoPlayBtn.style.display = 'inline-block';
    videoPauseBtn.style.display = 'none';
}

function nextVideo() {
    if (isShuffle) {
        const randomIndex = Math.floor(Math.random() * videos.length);
        loadVideo(randomIndex, true);
    } else {
        currentVideoIndex = (currentVideoIndex + 1) % videos.length;
        loadVideo(currentVideoIndex, true);
    }
}

function prevVideo() {
    currentVideoIndex = (currentVideoIndex - 1 + videos.length) % videos.length;
    loadVideo(currentVideoIndex, true);
}

function toggleShuffle() {
    isShuffle = !isShuffle;
    videoShuffleBtn.style.background = isShuffle ? '#00bcd4' : '#333';
}

function toggleRepeat() {
    isRepeat = !isRepeat;
    videoRepeatBtn.style.background = isRepeat ? '#00bcd4' : '#333';
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        videoPlayer.requestFullscreen().catch(err => console.error(err));
    } else {
        document.exitFullscreen();
    }
}

videoPlayBtn.addEventListener('click', playVideo);
videoPauseBtn.addEventListener('click', pauseVideo);
videoNextBtn.addEventListener('click', nextVideo);
videoPrevBtn.addEventListener('click', prevVideo);
videoFullscreenBtn.addEventListener('click', toggleFullscreen);
videoShuffleBtn.addEventListener('click', toggleShuffle);
videoRepeatBtn.addEventListener('click', toggleRepeat);

videoVolumeSlider.addEventListener('input', function() {
    videoPlayer.volume = this.value / 100;
});

videoPlayer.addEventListener('timeupdate', function() {
    const currentTime = videoPlayer.currentTime;
    const duration = videoPlayer.duration;
    if (duration) {
        const progressPercent = (currentTime / duration) * 100;
        videoProgress.style.width = `${progressPercent}%`;
        videoCurrentTimeEl.textContent = formatTime(currentTime);
    }
});

document.querySelector('.video-progress-container .progress-bar').addEventListener('click', function(e) {
    const progressBar = this;
    const clickPosition = e.offsetX;
    const progressBarWidth = progressBar.offsetWidth;
    const seekTime = (clickPosition / progressBarWidth) * videoPlayer.duration;
    videoPlayer.currentTime = seekTime;
});

// Event saat video selesai
videoPlayer.addEventListener('ended', function() {
    if (isRepeat) {
        videoPlayer.currentTime = 0;
        playVideo();
    } else {
        nextVideo();
    }
});

playlistItems.forEach((item, index) => {
    item.querySelector('.play-track').addEventListener('click', function() {
        loadVideo(index, true);
    });
});

// Awal: tidak autoplay
if (videos.length > 0) {
    loadVideo(0, false);
}

function playVideo(filename) {
    const video = document.getElementById("video-player");
    const source = document.getElementById("video-source");
    const current = document.getElementById("current-video");

    source.src = `/media/video/${filename}`;
    video.load();
    video.play();

    current.textContent = filename;
}