document.addEventListener("DOMContentLoaded", () => {

    const checkBtn = document.getElementById("check-update-btn");
    const updateBtn = document.getElementById("apply-update-btn");
    const statusBox = document.getElementById("update-status");
    const logBox = document.getElementById("update-log");

    // ===========================
    // Cek Update
    // ===========================
    checkBtn.addEventListener("click", async () => {
        statusBox.style.display = "block";
        statusBox.textContent = "Memeriksa pembaruan...";
        statusBox.style.background = "rgba(0,150,255,0.4)";

        const res = await fetch("/api/check-update");
        const result = await res.json();

        if (result.update_available) {
            statusBox.textContent = "Update tersedia!";
            statusBox.style.background = "rgba(0,255,100,0.4)";
            updateBtn.classList.remove("hidden");
        } else {
            statusBox.textContent = "Sudah versi terbaru.";
            statusBox.style.background = "rgba(255,50,50,0.4)";
        }
    });

    // ===========================
    // Terapkan Update
    // ===========================
    updateBtn.addEventListener("click", () => {
        updateBtn.classList.add("hidden");
        logBox.classList.remove("hidden");
        logBox.textContent = "Memulai update...\n";

        const ws = new WebSocket("ws://" + window.location.host + "/ws/update");

        ws.onmessage = (event) => {
            logBox.textContent += event.data + "\n";
            logBox.scrollTop = logBox.scrollHeight;
        };

        ws.onclose = () => {
            logBox.textContent += "\nUpdate selesai!";
        };
    });

});