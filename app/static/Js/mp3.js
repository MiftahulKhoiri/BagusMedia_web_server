document.addEventListener("DOMContentLoaded", () => {

    const items = document.querySelectorAll(".music-item");
    const playerBar = document.getElementById("player-bar");
    const audio = document.getElementById("audio-player");

    items.forEach(item => {
        item.addEventListener("click", () => {
            const filename = item.dataset.file;

            audio.src = `/media/mp3/${filename}`;
            audio.play();

            playerBar.style.display = "block";
        });
    });

});