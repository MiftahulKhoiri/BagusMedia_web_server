// video-list.js
// Singkat, jelas: klik item -> buka player bawah dan mainkan video.

document.addEventListener("DOMContentLoaded", () => {

    const items = document.querySelectorAll(".video-item");
    const playerBox = document.getElementById("video-player-box");
    const videoEl = document.getElementById("video-player");
    const closeBtn = document.getElementById("close-player");

    // Fungsi untuk buka player dan set src
    function openPlayer(filename) {
        // set sumber video via route /media/video/<filename>
        videoEl.src = `/media/video/${encodeURIComponent(filename)}`;
        videoEl.load();
        videoEl.play().catch(()=>{ /* bisa saja autoplay diblokir oleh browser */ });

        playerBox.style.display = "flex";
        playerBox.setAttribute("aria-hidden", "false");
        // scroll ke tampilan player (opsional)
        playerBox.scrollIntoView({ behavior: "smooth", block: "end" });
    }

    // Tutup player
    function closePlayer() {
        videoEl.pause();
        videoEl.src = "";
        playerBox.style.display = "none";
        playerBox.setAttribute("aria-hidden", "true");
    }

    // Pasang event click di tiap item
    items.forEach(item => {
        item.addEventListener("click", (e) => {
            // jika tombol play diklik, juga trigger open
            const filename = item.dataset.file;
            if (!filename) return;
            openPlayer(filename);
        });

        // tombol kecil play juga ada di dalam item, biar aman mencegah doble event
        const btn = item.querySelector(".btn-play");
        if (btn) {
            btn.addEventListener("click", (ev) => {
                ev.stopPropagation(); // jangan bubble ke item
                const filename = item.dataset.file;
                if (!filename) return;
                openPlayer(filename);
            });
        }
    });

    // event tombol tutup
    closeBtn.addEventListener("click", () => closePlayer());

    // ESC untuk menutup
    document.addEventListener("keydown", (ev) => {
        if (ev.key === "Escape") closePlayer();
    });

    // Jika video selesai, biarkan player tetap terbuka (atau bisa auto-close jika suka)
    videoEl.addEventListener("ended", () => {
        // contoh: tetap terbuka, tapi bisa dikosongkan src jika mau
        // closePlayer();
    });
});