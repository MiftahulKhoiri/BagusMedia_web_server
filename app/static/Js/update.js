document.addEventListener("DOMContentLoaded", () => {

    const checkBtn = document.getElementById("check-update-btn");
    const updateBtn = document.getElementById("run-update-btn");
    const output = document.getElementById("update-output");

    /* ==========================
       CEK UPDATE
    =========================== */
    checkBtn.addEventListener("click", async () => {
        output.textContent = "Memeriksa update...\n";

        const res = await fetch("/api/check-update");
        const result = await res.json();

        if (result.error) {
            output.textContent += "Error: " + result.error;
            return;
        }

        output.textContent += result.output;

        if (result.update_available) {
            output.textContent += "\n🚀 Update tersedia!";
            updateBtn.disabled = false;
        } else {
            output.textContent += "\n✔ Sistem sudah terbaru.";
            updateBtn.disabled = true;
        }
    });

    /* ==========================
       JALANKAN UPDATE
    =========================== */
    updateBtn.addEventListener("click", () => {

        output.textContent = "Menjalankan update...\n";

        const ws = new WebSocket("ws://" + window.location.host + "/ws/update");

        ws.onmessage = (event) => {
            output.textContent += event.data + "\n";
        };

        ws.onclose = () => {
            output.textContent += "\n[WS CLOSED]";
        };
    });

});