// static/Js/mp3.js
document.addEventListener("DOMContentLoaded", () => {

  // ========================
  // ELEMENTS
  // ========================
  const playlistEls = Array.from(document.querySelectorAll(".sm-track"));
  const audio = document.getElementById("audio-player");

  // mini player
  const mini = document.getElementById("mini-player");
  const miniTitle = document.getElementById("mini-title");
  const miniArtist = document.getElementById("mini-artist");
  const miniCoverEl = document.getElementById("mini-cover");
  const miniPlay = document.getElementById("mini-play");
  const miniPrev = document.getElementById("mini-prev");
  const miniNext = document.getElementById("mini-next");

  // full player
  const full = document.getElementById("full-player");
  const fullTitle = document.getElementById("full-title");
  const fullArtist = document.getElementById("full-artist");
  const fullCoverEl = document.getElementById("full-cover");
  const closeFull = document.getElementById("close-full");

  // full player buttons
  const playBtn = document.getElementById("play-btn");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  // progress & volume
  const progress = document.getElementById("progress");
  const currentTimeEl = document.getElementById("current-time");
  const durationEl = document.getElementById("duration");
  const progressOuter = document.getElementById("progress-outer");
  const volumeSlider = document.getElementById("volume-slider");

  // background blur
  const bgBlur = document.getElementById("player-bg-blur");

  // ========================
  // STATE
  // ========================
  let idx = 0;
  const tracks = playlistEls.map(el => el.dataset.src);
  const titles = playlistEls.map(el => el.querySelector(".track-title").textContent.trim());
  let isPlaying = false;
  let isShuffle = false;
  let isRepeat = false;

  if (!audio) return;

  // ========================
  // HELPERS
  // ========================
  function formatTime(sec){
    if (!sec || isNaN(sec)) return "0:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60).toString().padStart(2,"0");
    return `${m}:${s}`;
  }

  function filenameFromSrc(src){
    try{
      const p = src.split("/");
      return decodeURIComponent(p[p.length - 1]);
    }catch{
      return src;
    }
  }

  // ========================================
  // 🎨 1. EXTRACT DOMINANT COLOR FROM IMAGE
  // ========================================
  function extractColor(imageUrl, callback){
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = imageUrl;

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = img.width;
      canvas.height = img.height;

      ctx.drawImage(img, 0, 0);

      const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;

      let r = 0, g = 0, b = 0, count = 0;

      for (let i = 0; i < data.length; i += 4 * 40) {
        r += data[i];
        g += data[i + 1];
        b += data[i + 2];
        count++;
      }

      r = Math.floor(r / count);
      g = Math.floor(g / count);
      b = Math.floor(b / count);

      callback(`rgb(${r}, ${g}, ${b})`);
    };

    img.onerror = () => callback("rgb(80,80,80)");
  }

  // ========================================
  // 🎨 2. APPLY COLOR THEME TO CSS VARIABLES
  // ========================================
  function applyTheme(color){
    const root = document.documentElement;

    // Ubah warna utama
    root.style.setProperty("--accent", color);

    // Buat warna kedua (lebih gelap)
    root.style.setProperty("--accent-2", color);

    // shadow soft
    root.style.setProperty("--accent-soft", color.replace("rgb", "rgba").replace(")", ",0.25)"));
  }

  // ========================
  // PLAYLIST CLICK
  // ========================
  playlistEls.forEach((el, i) => {
    const btn = el.querySelector(".track-play-btn");
    el.addEventListener("click", () => startTrack(i));
    if (btn) btn.addEventListener("click", (e) => {
      e.stopPropagation();
      startTrack(i);
    });
  });

  // ========================
  // START TRACK
  // ========================
  function startTrack(i){
    if (!tracks.length) return;

    idx = i;
    const src = tracks[idx];
    const title = titles[idx] || "Unknown";

    miniTitle.textContent = title;
    fullTitle.textContent = title;

    miniArtist.textContent = "Unknown Artist";
    fullArtist.textContent = "Unknown Artist";

    mini.classList.remove("collapsed");

    // COVER
    const filename = filenameFromSrc(src);
    const coverUrl = "/media/cover/mp3/" + encodeURIComponent(filename);

    miniCoverEl.src = coverUrl;
    fullCoverEl.src = coverUrl;

    // BLUR BG
    if (bgBlur){
      bgBlur.style.backgroundImage = `url('${coverUrl}')`;
      bgBlur.style.opacity = "1";
    }

    // 🎨 APPLY DYNAMIC THEME
    extractColor(coverUrl, (color) => {
      applyTheme(color);
    });

    // PLAY
    audio.src = src;
    audio.load();

    audio.oncanplay = () => {
      audio.play().then(() => {
        isPlaying = true;
        updatePlayButtons(true);
        highlightPlaying();
      });
    };
  }

  // ========================
  // UI UPDATES
  // ========================
  function highlightPlaying(){
    playlistEls.forEach((el, i) => {
      el.classList.toggle("playing", i === idx);
    });
  }

  function updatePlayButtons(playing){
    miniPlay.textContent = playing ? "⏸" : "▶";
    playBtn.textContent = playing ? "⏸" : "▶";
  }

  // ========================
  // MINI PLAYER CONTROLS
  // ========================
  miniPlay.addEventListener("click", () => {
    if (audio.paused) audio.play(), updatePlayButtons(true);
    else audio.pause(), updatePlayButtons(false);
  });

  miniPrev.addEventListener("click", prevTrack);
  miniNext.addEventListener("click", nextTrack);

  mini.addEventListener("click", (e) => {
    if (e.target.closest(".mini-right")) return;
    full.classList.remove("hidden");
  });

  closeFull.addEventListener("click", () => {
    full.classList.add("hidden");
  });

  // ========================
  // FULL PLAYER CONTROLS
  // ========================
  playBtn.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused) audio.play(), updatePlayButtons(true);
    else audio.pause(), updatePlayButtons(false);
  });

  prevBtn.addEventListener("click", prevTrack);
  nextBtn.addEventListener("click", nextTrack);

  function prevTrack(){
    idx = (idx - 1 + tracks.length) % tracks.length;
    startTrack(idx);
  }

  function nextTrack(){
    idx = (idx + 1) % tracks.length;
    startTrack(idx);
  }

  // ========================
  // PROGRESS
  // ========================
  audio.addEventListener("timeupdate", () => {
    if (!audio.duration) return;

    const pct = (audio.currentTime / audio.duration) * 100;
    progress.style.width = pct + "%";

    currentTimeEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
  });

  progressOuter.addEventListener("click", (e) => {
    const r = progressOuter.getBoundingClientRect();
    const pct = (e.clientX - r.left) / r.width;
    audio.currentTime = pct * audio.duration;
  });

  // ========================
  // VOLUME
  // ========================
  volumeSlider.addEventListener("input", (e) => {
    audio.volume = e.target.value / 100;
  });

  audio.addEventListener("ended", nextTrack);

});