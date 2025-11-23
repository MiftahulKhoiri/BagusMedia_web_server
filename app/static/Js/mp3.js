// static/Js/mp3.js
document.addEventListener("DOMContentLoaded", () => {
  // elements
  const playlistEls = Array.from(document.querySelectorAll(".sm-track"));
  const audio = document.getElementById("audio-player");
  const mini = document.getElementById("mini-player");
  const miniTitle = document.getElementById("mini-title");
  const miniArtist = document.getElementById("mini-artist");
  const miniPlay = document.getElementById("mini-play");
  const miniPrev = document.getElementById("mini-prev");
  const miniNext = document.getElementById("mini-next");

  const full = document.getElementById("full-player");
  const closeFull = document.getElementById("close-full");
  const fullTitle = document.getElementById("full-title");
  const fullArtist = document.getElementById("full-artist");
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

  // safety
  if (!audio) return;

  // helper
  function formatTime(sec){
    if (!sec || isNaN(sec)) return "0:00";
    const m = Math.floor(sec/60);
    const s = Math.floor(sec%60).toString().padStart(2,"0");
    return `${m}:${s}`;
  }

  // attach click on each track
  playlistEls.forEach((el, i) => {
    const btn = el.querySelector(".track-play-btn");
    el.addEventListener("click", (e) => {
      // prefer clicking whole item
      e.preventDefault();
      startTrack(i);
    });
    if (btn) btn.addEventListener("click", (e) => {
      e.stopPropagation();
      startTrack(i);
    });
  });

  // start playing a track (android-friendly)
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
    // show mini
    if (mini && mini.classList.contains("collapsed")) {
      mini.classList.remove("collapsed");
    }

    // set src and load
    audio.src = src;
    audio.load();
    // ensure play after media can play
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

  // highlight current track in list
  function highlightPlaying(){
    playlistEls.forEach((el, i) => {
      el.classList.toggle("playing", i === idx);
    });
  }

  // update play/pause icons in mini & full
  function updatePlayButtons(playing){
    // mini
    if (mini) {
      const btn = document.getElementById("mini-play");
      if (btn) btn.textContent = playing ? "⏸" : "▶";
    }
    // full center button
    if (playBtn) playBtn.textContent = playing ? "⏸" : "▶";
  }

  // mini controls
  if (miniPlay) miniPlay.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused) audio.play().then(()=>{isPlaying=true;updatePlayButtons(true)}).catch(()=>{});
    else audio.pause(), isPlaying=false, updatePlayButtons(false);
  });
  if (miniPrev) miniPrev.addEventListener("click", () => {
    prevTrack();
  });
  if (miniNext) miniNext.addEventListener("click", () => {
    nextTrack();
  });

  // open full player
  mini.addEventListener("click", (e) => {
    // don't expand when clicking the small control buttons (they have pointer-events)
    if (e.target.closest(".mini-right")) return;
    full.classList.remove("hidden");
    full.setAttribute("aria-hidden","false");
  });

  // close full
  if (closeFull) closeFull.addEventListener("click", () => {
    full.classList.add("hidden");
    full.setAttribute("aria-hidden","true");
  });

  // full player controls
  if (playBtn) playBtn.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused) audio.play().then(()=>{isPlaying=true;updatePlayButtons(true)}).catch(()=>{});
    else audio.pause(), isPlaying=false, updatePlayButtons(false);
  });
  if (prevBtn) prevBtn.addEventListener("click", prevTrack);
  if (nextBtn) nextBtn.addEventListener("click", nextTrack);

  // prev/next logic
  function prevTrack(){
    if (isShuffle) {
      idx = Math.floor(Math.random()*tracks.length);
    } else {
      idx = (idx - 1 + tracks.length) % tracks.length;
    }
    startTrack(idx);
  }
  function nextTrack(){
    if (isRepeat) { startTrack(idx); return; }
    if (isShuffle) idx = Math.floor(Math.random()*tracks.length);
    else idx = (idx + 1) % tracks.length;
    startTrack(idx);
  }

  // audio progress
  audio.addEventListener("timeupdate", () => {
    if (!audio.duration) return;
    const pct = (audio.currentTime / audio.duration) * 100;
    progress.style.width = pct + "%";
    currentTimeEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
  });

  // seek on progress bar
  if (progressOuter) progressOuter.addEventListener("click", (e) => {
    const rect = progressOuter.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, x / rect.width));
    if (audio.duration) audio.currentTime = pct * audio.duration;
  });

  // volume
  if (volumeSlider) volumeSlider.addEventListener("input", (e) => {
    audio.volume = e.target.value / 100;
  });

  // ended
  audio.addEventListener("ended", () => {
    nextTrack();
  });

  // init volume default
  if (volumeSlider) audio.volume = volumeSlider.value / 100;

  // expose debug
  window._mp3 = { startTrack, nextTrack, prevTrack, tracks };

});