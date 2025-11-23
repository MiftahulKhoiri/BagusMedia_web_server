// static/Js/mp3.js
document.addEventListener("DOMContentLoaded", () => {
  // elements
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
  const closeFull = document.getElementById("close-full");
  const fullTitle = document.getElementById("full-title");
  const fullArtist = document.getElementById("full-artist");
  const fullCoverEl = document.getElementById("full-cover");

  const playBtn = document.getElementById("play-btn");
  const pauseBtn = document.getElementById("pause-btn");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");

  const progress = document.getElementById("progress");
  const currentTimeEl = document.getElementById("current-time");
  const durationEl = document.getElementById("duration");
  const progressOuter = document.getElementById("progress-outer");
  const volumeSlider = document.getElementById("volume-slider");

  // state
  let idx = 0;
  const tracks = playlistEls.map(el => el.dataset.src);
  const titles = playlistEls.map(el => el.querySelector(".track-title").textContent.trim());
  let isPlaying = false;
  let isShuffle = false;
  let isRepeat = false;

  if (!audio) return;

  // helper
  function formatTime(sec){
    if (!sec || isNaN(sec)) return "0:00";
    const m = Math.floor(sec/60);
    const s = Math.floor(sec%60).toString().padStart(2,"0");
    return `${m}:${s}`;
  }

  // Ambil nama file dari URL src
  function filenameFromSrc(src){
    try{
      const p = src.split("/");
      return decodeURIComponent(p[p.length - 1]);
    }catch{
      return src;
    }
  }

  // klik playlist
  playlistEls.forEach((el, i) => {
    const btn = el.querySelector(".track-play-btn");

    el.addEventListener("click", (e) => {
      e.preventDefault();
      startTrack(i);
    });

    if (btn) btn.addEventListener("click", (e) => {
      e.stopPropagation();
      startTrack(i);
    });
  });

  // PLAY TRACK
  function startTrack(i){
    if (!tracks.length) return;

    idx = i;
    const src = tracks[idx];
    const title = titles[idx] || "Unknown";

    // update UI
    miniTitle.textContent = title;
    fullTitle.textContent = title;
    miniArtist.textContent = "Unknown Artist";
    fullArtist.textContent = "Unknown Artist";

    // tampilkan mini player
    mini.classList.remove("collapsed");

    // ==== COVER HERE ====
    const filename = filenameFromSrc(src);
    const coverUrl = "/media/cover/mp3/" + encodeURIComponent(filename);

    if (miniCoverEl) miniCoverEl.src = coverUrl;
    if (fullCoverEl) fullCoverEl.src = coverUrl;
    // =====================

    audio.src = src;
    audio.load();

    audio.oncanplay = () => {
      audio.play().then(() => {
        isPlaying = true;
        updatePlayButtons(true);
        highlightPlaying();
      }).catch(err => {
        console.log("PLAY ERR:", err);
        updatePlayButtons(false);
      });
    };
  }

  function highlightPlaying(){
    playlistEls.forEach((el, i) => {
      el.classList.toggle("playing", i === idx);
    });
  }

  function updatePlayButtons(playing){
    if (miniPlay) miniPlay.textContent = playing ? "⏸" : "▶";
    if (playBtn) playBtn.textContent = playing ? "⏸" : "▶";
  }

  // MINI PLAYER controls
  if (miniPlay) miniPlay.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused){
      audio.play().then(()=>{isPlaying=true;updatePlayButtons(true)}).catch(()=>{});
    } else {
      audio.pause();
      isPlaying = false;
      updatePlayButtons(false);
    }
  });

  if (miniPrev) miniPrev.addEventListener("click", prevTrack);
  if (miniNext) miniNext.addEventListener("click", nextTrack);

  // open full view
  mini.addEventListener("click", (e) => {
    if (e.target.closest(".mini-right")) return;
    full.classList.remove("hidden");
  });

  if (closeFull) closeFull.addEventListener("click", () => {
    full.classList.add("hidden");
  });

  // FULL CONTROLS
  if (playBtn) playBtn.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused){
      audio.play().then(()=>{isPlaying=true;updatePlayButtons(true)}).catch(()=>{});
    } else {
      audio.pause();
      isPlaying=false;
      updatePlayButtons(false);
    }
  });

  if (prevBtn) prevBtn.addEventListener("click", prevTrack);
  if (nextBtn) nextBtn.addEventListener("click", nextTrack);

  // PREV / NEXT logic
  function prevTrack(){
    if (isShuffle) idx = Math.floor(Math.random() * tracks.length);
    else idx = (idx - 1 + tracks.length) % tracks.length;
    startTrack(idx);
  }

  function nextTrack(){
    if (isRepeat) startTrack(idx);
    else if (isShuffle) idx = Math.floor(Math.random() * tracks.length);
    else idx = (idx + 1) % tracks.length;
    startTrack(idx);
  }

  // progress bar
  audio.addEventListener("timeupdate", () => {
    if (!audio.duration) return;
    const pct = (audio.currentTime / audio.duration) * 100;
    progress.style.width = pct + "%";

    currentTimeEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
  });

  // seek
  if (progressOuter && progressOuter.addEventListener)
    progressOuter.addEventListener("click", (e) => {
      const rect = progressOuter.getBoundingClientRect();
      const pct = (e.clientX - rect.left) / rect.width;
      if (audio.duration) audio.currentTime = pct * audio.duration;
    });

  // volume
  if (volumeSlider)
    volumeSlider.addEventListener("input", (e) => {
      audio.volume = e.target.value / 100;
    });

  audio.addEventListener("ended", () => {
    nextTrack();
  });

  // default volume
  if (volumeSlider) audio.volume = volumeSlider.value / 100;

  window._mp3 = { startTrack, nextTrack, prevTrack, tracks };
});