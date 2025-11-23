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

  // buttons
  const playBtn = document.getElementById("play-btn");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const shuffleBtn = document.getElementById("shuffle-btn");
  const repeatBtn = document.getElementById("repeat-btn");

  // progress
  const progress = document.getElementById("progress");
  const currentTimeEl = document.getElementById("current-time");
  const durationEl = document.getElementById("duration");
  const progressOuter = document.getElementById("progress-outer");

  // volume
  const volumeSlider = document.getElementById("volume-slider");

  // blur bg
  const bgBlur = document.getElementById("player-bg-blur");

  // lirik
  const lyricsBox = document.getElementById("lyrics-lines");

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
    try {
      const p = src.split("/");
      return decodeURIComponent(p[p.length - 1]);
    } catch {
      return src;
    }
  }

  // ========================
  // LRC SYSTEM
  // ========================
  async function loadLyrics(filename) {
    const url = "/media/lyrics/mp3/" + encodeURIComponent(filename);

    try {
      const res = await fetch(url);
      if (!res.ok) {
        lyricsBox.innerHTML = "<p class='no-lyrics'>Tidak ada lirik</p>";
        return [];
      }

      const text = await res.text();
      return parseLRC(text);

    } catch {
      lyricsBox.innerHTML = "<p class='no-lyrics'>Tidak ada lirik</p>";
      return [];
    }
  }

  function parseLRC(text) {
    const lines = text.split("\n");
    const parsed = [];

    for (let line of lines) {
      const match = line.match(/\[(\d+):(\d+\.\d+)\](.*)/);
      if (!match) continue;

      const min = parseInt(match[1]);
      const sec = parseFloat(match[2]);
      const time = min * 60 + sec;
      const lyric = match[3].trim();

      parsed.push({ time, lyric });
    }

    return parsed;
  }

  function highlightLyrics(lyrics, currentTime) {
    let activeIndex = -1;

    for (let i = 0; i < lyrics.length; i++) {
      if (currentTime >= lyrics[i].time) activeIndex = i;
    }

    [...lyricsBox.children].forEach((el, i) => {
      el.classList.toggle("active", i === activeIndex);
    });

    if (activeIndex >= 0) {
      lyricsBox.children[activeIndex].scrollIntoView({
        behavior: "smooth",
        block: "center"
      });
    }
  }

  // ========================
  // APPLY PRIMARY COLOR
  // ========================
  function applyThemeColor(color){
    document.documentElement.style.setProperty("--accent", color);
    document.documentElement.style.setProperty("--accent-2", color);
    progress.style.background = `linear-gradient(90deg, ${color}, ${color})`;
    playBtn.style.background = color;
  }

  // ========================
  // START TRACK
  // ========================
  function startTrack(i){
    idx = i;

    const src = tracks[idx];
    const title = titles[idx] || "Unknown";
    const filename = filenameFromSrc(src);

    const coverUrl = "/media/cover/mp3/" + encodeURIComponent(filename);

    miniTitle.textContent = title;
    fullTitle.textContent = title;
    miniArtist.textContent = "Unknown Artist";
    fullArtist.textContent = "Unknown Artist";

    mini.classList.remove("collapsed");

    // COVER SET
    if (miniCoverEl) miniCoverEl.src = coverUrl;
    if (fullCoverEl) fullCoverEl.src = coverUrl;

    // BLUR BG
    if (bgBlur){
      bgBlur.style.backgroundImage = `url('${coverUrl}')`;
      bgBlur.style.opacity = "1";
    }

    // COLOR EXTRACT
    setTimeout(() => extractColorFromImage(fullCoverEl), 50);

    // LYRICS
    loadLyrics(filename).then((lyrics) => {
      lyricsBox.innerHTML = "";
      lyrics.forEach(line => {
        const p = document.createElement("p");
        p.textContent = line.lyric;
        lyricsBox.appendChild(p);
      });

      audio.ontimeupdate = () => {
        highlightLyrics(lyrics, audio.currentTime);
      };
    });

    // PLAY
    audio.src = src;
    audio.load();
    audio.oncanplay = () => {
      audio.play();
      isPlaying = true;
      updatePlayButtons(true);
      highlightPlaying();
    };
  }

  // ========================
  // COLOR EXTRACTION
  // ========================
  function extractColorFromImage(img){
    try{
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      const data = ctx.getImageData(0,0,canvas.width,canvas.height).data;

      let r=0,g=0,b=0,count=0;
      for(let i=0;i<data.length;i+=40){
        r+=data[i];
        g+=data[i+1];
        b+=data[i+2];
        count++;
      }
      r=Math.floor(r/count);
      g=Math.floor(g/count);
      b=Math.floor(b/count);

      applyThemeColor(`rgb(${r},${g},${b})`);

    }catch(e){
      console.log("No color extract:",e);
    }
  }

  // ========================
  // UI
  // ========================
  function highlightPlaying(){
    playlistEls.forEach((el,i)=>{
      el.classList.toggle("playing", i===idx);
    });
  }

  function updatePlayButtons(playing){
    miniPlay.textContent = playing ? "⏸" : "▶";
    playBtn.textContent = playing ? "⏸" : "▶";
  }

  // ========================
  // PLAYLIST CLICK
  // ========================
  playlistEls.forEach((el,i)=>{
    el.addEventListener("click", ()=> startTrack(i));
  });

  // ========================
  // MINI PLAYER
  // ========================
  miniPlay.addEventListener("click", ()=>{
    if (!audio.src) return;

    if (audio.paused){
      audio.play();
      updatePlayButtons(true);
    } else {
      audio.pause();
      updatePlayButtons(false);
    }
  });

  miniPrev.addEventListener("click", prevTrack);
  miniNext.addEventListener("click", nextTrack);

  mini.addEventListener("click",(e)=>{
    if (!e.target.closest(".mini-right")){
      full.classList.remove("hidden");
    }
  });

  closeFull.addEventListener("click",()=>{
    full.classList.add("hidden");
  });

  // ========================
  // FULL PLAYER CONTROLS
  // ========================
  playBtn.addEventListener("click", () => {
    if (!audio.src) return;

    if (audio.paused){
      audio.play();
      updatePlayButtons(true);
    } else {
      audio.pause();
      updatePlayButtons(false);
    }
  });

  prevBtn.addEventListener("click", prevTrack);
  nextBtn.addEventListener("click", nextTrack);

  shuffleBtn.addEventListener("click", ()=>{
    isShuffle = !isShuffle;
    shuffleBtn.style.opacity = isShuffle ? "1" : ".4";
  });

  repeatBtn.addEventListener("click", ()=>{
    isRepeat = !isRepeat;
    repeatBtn.style.opacity = isRepeat ? "1" : ".4";
  });

  function prevTrack(){
    idx = isShuffle ?
      Math.floor(Math.random()*tracks.length) :
      (idx - 1 + tracks.length) % tracks.length;

    startTrack(idx);
  }

  function nextTrack(){
    if (isRepeat) return startTrack(idx);

    idx = isShuffle ?
      Math.floor(Math.random()*tracks.length) :
      (idx + 1) % tracks.length;

    startTrack(idx);
  }

  // ========================
  // PROGRESS
  // ========================
  audio.addEventListener("timeupdate", ()=>{
    if (!audio.duration) return;

    const pct = (audio.currentTime / audio.duration) * 100;
    progress.style.width = pct + "%";

    currentTimeEl.textContent = formatTime(audio.currentTime);
    durationEl.textContent = formatTime(audio.duration);
  });

  progressOuter.addEventListener("click",(e)=>{
    const rect = progressOuter.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    audio.currentTime = pct * audio.duration;
  });

  // ========================
  // VOLUME
  // ========================
  volumeSlider.addEventListener("input",(e)=>{
    audio.volume = e.target.value / 100;
  });
  audio.volume = volumeSlider.value / 100;

  audio.addEventListener("ended", nextTrack);

  // expose for debug
  window._mp3 = { startTrack, nextTrack, prevTrack, tracks };
});