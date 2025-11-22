document.addEventListener("DOMContentLoaded", () => {

    const audio = document.getElementById("audio");
    const playlist = document.querySelectorAll(".track");

    const title = document.getElementById("title");
    const playBtn = document.getElementById("play");
    const pauseBtn = document.getElementById("pause");
    const nextBtn = document.getElementById("next");
    const prevBtn = document.getElementById("prev");
    const progressBar = document.getElementById("progress");

    let index = 0;
    let srcList = [];

    playlist.forEach((item, i) => {
        srcList.push(item.dataset.src);

        item.addEventListener("click", () => {
            playTrack(i);
        });
    });

    function playTrack(i) {
        index = i;

        let item = playlist[index];
        let src = srcList[index];

        title.textContent = item.textContent.trim();
        audio.src = src;

        audio.load();
        audio.oncanplay = () => {
            audio.play();
        };

        highlight(index);
    }

    function highlight(i) {
        playlist.forEach(p => p.classList.remove("playing"));
        playlist[i].classList.add("playing");
    }

    playBtn.addEventListener("click", () => audio.play());
    pauseBtn.addEventListener("click", () => audio.pause());

    nextBtn.addEventListener("click", () => {
        index = (index + 1) % srcList.length;
        playTrack(index);
    });

    prevBtn.addEventListener("click", () => {
        index = (index - 1 + srcList.length) % srcList.length;
        playTrack(index);
    });

    audio.addEventListener("timeupdate", () => {
        if (!audio.duration) return;
        let percent = (audio.currentTime / audio.duration) * 100;
        progressBar.style.width = percent + "%";
    });

});