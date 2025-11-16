document.addEventListener("DOMContentLoaded", () => {

    const items = document.querySelectorAll(".mp3-item");
    const playerBox = document.getElementById("player-box");
    const audioPlayer = document.getElementById("audio-player");

    items.forEach(item => {
        item.addEventListener("click", () => {

            const filename = item.dataset.file;

            // Set audio sumber
            audioPlayer.src = `/media/mp3/${filename}`;
            audioPlayer.play();

            // Tampilkan player
            playerBox.style.display = "block";

            // Hapus highlight sebelumnya
            items.forEach(i => i.classList.remove("active"));

            // Tambahkan highlight ke item aktif
            item.classList.add("active");
        });
    });

});