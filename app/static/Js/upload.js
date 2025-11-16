document.addEventListener("DOMContentLoaded", () => {

    const uploadArea = document.getElementById("upload-area");
    const fileInput = document.getElementById("file-input");
    const progressContainer = document.getElementById("upload-progress");

    // Klik area → buka file picker
    uploadArea.addEventListener("click", () => fileInput.click());

    // Handle file terpilih
    fileInput.addEventListener("change", () => {
        const files = fileInput.files;
        if (files.length > 0) {
            startUpload(files);
        }
    });

    // Fungsi upload berurutan
    async function startUpload(files) {
        progressContainer.innerHTML = "";

        for (const file of files) {
            const item = createProgressItem(file.name);
            progressContainer.appendChild(item);

            await uploadSingle(file, item);
        }
    }

    // Buat UI progress
    function createProgressItem(filename) {
        const div = document.createElement("div");
        div.classList.add("progress-item");

        div.innerHTML = `
            <div class="progress-info">
                <span>${filename}</span>
                <span class="status">Menunggu...</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>`;
        return div;
    }

    // Upload file
    async function uploadSingle(file, item) {
        const status = item.querySelector(".status");
        const fill = item.querySelector(".progress-fill");

        status.textContent = "Mengupload...";

        const fd = new FormData();
        fd.append("files", file);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: fd
            });

            const result = await res.json();

            if (result.results && result.results[0].status === "success") {
                status.textContent = "Selesai ✓";
                status.classList.add("success");
                fill.style.width = "100%";
                fill.classList.add("success");
            } else {
                throw new Error("Gagal upload");
            }

        } catch (err) {
            status.textContent = "Gagal ✗";
            fill.classList.add("error");
        }
    }

});