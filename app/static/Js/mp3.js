// static/Js/mp3.js
// Safe-init: tunggu DOM ready agar elemen yang di-HTML (termasuk mini-player) sudah ada.
document.addEventListener("DOMContentLoaded", () => {
  // =========================================================
  // 🎧 Pemutar Musik MP3 - BAGUS MEDIA SERVER (robust init)
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
  const playlist = document.getElementById('playlist') || document.querySelector('.playlist');
  const playlistItems = playlist ? Array.from(playlist.querySelectorAll('.playlist-item')) : [];
  const visualizer = document.querySelector('.visualizer');
  const shuffleStatus = document.getElementById('shuffle-status');
  const repeatStatus = document.getElementById('repeat-status');

  // mini-player elements (may exist below script tag)
  const mini = document.getElementById("mini-player");
  const miniTitle = document.getElementById("mini-title");
  const miniPrev = document.getElementById("mini-prev");
  const miniPlay = document.getElementById("mini-play");
  const miniPause = document.getElementById("mini-pause");
  const miniNext = document.getElementById("mini-next");
  const miniClose = document.getElementById("mini-close");

  let currentIndex = 0;
  let isShuffle = false;
  let isRepeat = false;

  // 🎵 Daftar lagu dari playlist
  const tracks = playlistItems.map(item => item.dataset.src);

  // safety: jika tidak ada audio element, abort
  if (!audio) return;

  // Fungsi memutar lagu
  function playTrack(index) {
      if (!tracks.length) return;
      if (index < 0) index = 0;
      if (index >= tracks.length) index = tracks.length - 1;
      currentIndex = index;
      const src = tracks[currentIndex];
      audio.src = src;
      audio.play().catch(()=>{});
      updateNowPlaying();
      highlightCurrent(src);
      if (visualizer) visualizer.classList.add('active');
      // update mini player
      if (mini && miniTitle) showMiniPlayer(playlistItems[currentIndex].querySelector('.track-name').textContent);
  }

  // Update judul lagu
  function updateNowPlaying() {
      if (!playlistItems[currentIndex]) return;
      const trackName = playlistItems[currentIndex].querySelector('.track-name').textContent;
      if (nowPlaying) nowPlaying.textContent = `🎧 Sedang diputar: ${trackName}`;
  }

  // Tombol Play / Pause
  if (playBtn) playBtn.onclick = () => {
      if (audio.src === '') playTrack(0);
      else audio.play().catch(()=>{});
      if (visualizer) visualizer.classList.add('active');
  };

  if (pauseBtn) pauseBtn.onclick = () => {
      audio.pause();
      if (visualizer) visualizer.classList.remove('active');
  };

  // Tombol Next / Prev
  if (nextBtn) nextBtn.onclick = () => {
      if (!tracks.length) return;
      if (isShuffle) currentIndex = Math.floor(Math.random() * tracks.length);
      else currentIndex = (currentIndex + 1) % tracks.length;
      playTrack(currentIndex);
  };

  if (prevBtn) prevBtn.onclick = () => {
      if (!tracks.length) return;
      currentIndex = (currentIndex - 1 + tracks.length) % tracks.length;
      playTrack(currentIndex);
  };

  // Shuffle & Repeat
  if (shuffleBtn) shuffleBtn.onclick = () => {
      isShuffle = !isShuffle;
      if (shuffleStatus) {
          shuffleStatus.textContent = `Shuffle: ${isShuffle ? 'On' : 'Off'}`;
          shuffleStatus.style.color = isShuffle ? '#0ff' : '#aaa';
      }
  };

  if (repeatBtn) repeatBtn.onclick = () => {
      isRepeat = !isRepeat;
      if (repeatStatus) {
          repeatStatus.textContent = `Repeat: ${isRepeat ? 'On' : 'Off'}`;
          repeatStatus.style.color = isRepeat ? '#ff00ff' : '#aaa';
      }
  };

  // Volume
  if (volumeSlider) volumeSlider.oninput = () => {
      audio.volume = volumeSlider.value / 100;
  };

  // Progress bar update
  audio.addEventListener('timeupdate', () => {
      if (!audio.duration || !progress) return;
      const percent = (audio.currentTime / audio.duration) * 100;
      progress.style.width = percent + '%';
      // update small current/duration if exists
      const ct = document.getElementById('current-time');
      const dt = document.getElementById('duration');
      if (ct) ct.textContent = formatTime(audio.currentTime);
      if (dt && audio.duration) dt.textContent = formatTime(audio.duration);
  });

  function formatTime(sec){
      if (!sec || isNaN(sec)) return "0:00";
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60).toString().padStart(2,'0');
      return `${m}:${s}`;
  }

  // Klik pada playlist
  playlistItems.forEach((item, index) => {
      const btn = item.querySelector('.play-track');
      if (btn) btn.addEventListener('click', (e) => {
          e.preventDefault();
          playTrack(index);
      });
  });

  // Jika lagu selesai
  audio.addEventListener('ended', () => {
      if (isRepeat) playTrack(currentIndex);
      else if (nextBtn) nextBtn.click();
  });

  // 🌙 Tema Toggle (jika ada)
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light');
      if (document.body.classList.contains('light')) {
          document.body.style.background = "radial-gradient(circle at center, #f0f0ff 0%, #cce0ff 100%)";
          themeToggle.textContent = "☀️";
      } else {
          document.body.style.background = "radial-gradient(circle at center, #000010 0%, #020111 100%)";
          themeToggle.textContent = "🌙";
      }
  });

  // ==========================
  // HIGHLIGHT CARD YANG DIPUTAR
  // ==========================
  function highlightCurrent(src) {
      document.querySelectorAll(".playlist-item").forEach(item => {
          item.classList.remove("playing");
          if (item.dataset.src === src) item.classList.add("playing");
      });
  }

  // ============================
  // MINI PLAYER LOGIC (safe)
  // ============================
  function showMiniPlayer(title){
      if (!mini) return;
      if (miniTitle) miniTitle.textContent = title || "—
";
      mini.classList.remove("hidden");
      mini.classList.add("visible");
  }

  if (miniClose) miniClose.onclick = () => mini.classList.add("hidden");

  if (miniPlay) miniPlay.onclick = () => audio.play().catch(()=>{});
  if (miniPause) miniPause.onclick = () => audio.pause();
  if (miniPrev) miniPrev.onclick = () => {
      if (typeof prevBtn !== 'undefined' && prevBtn) prevBtn.click();
  };
  if (miniNext) miniNext.onclick = () => {
      if (typeof nextBtn !== 'undefined' && nextBtn) nextBtn.click();
  };

  // expose a simple API for debugging
  window._mp3player = {
      playTrack, playIndex: (i)=>playTrack(i), currentIndex
  };

});

setInterval(() => {
  document.getElementById("debug-audio-url").textContent =
    "AUDIO URL: " + audio.src;
}, 500);