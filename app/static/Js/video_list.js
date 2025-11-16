document.addEventListener("DOMContentLoaded", () => {

    const items = document.querySelectorAll(".video-item");
    const playerBox = document.getElementById("video-player-box");
    const videoPlayer = document.getElementById("video-player");

    items.forEach(item => {
        item.addEventListener("click", () => {

            const filename = item.dataset.file;
            videoPlayer.src = `/media/video/${filename}`;
            videoPlayer.play();

            playerBox.style.display = "block";
        });
    });

});