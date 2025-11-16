document.addEventListener("DOMContentLoaded", () => {

    const fileInput = document.getElementById("file-input");
    const selectBtn = document.getElementById("select-btn");
    const uploadBtn = document.getElementById("upload-btn");
    const fileList = document.getElementById("file-list");

    let selectedFiles = [];

    /* ============================
       PILIH FILE
    ============================ */
    selectBtn.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        selectedFiles = Array.from(fileInput.files);

        fileList.innerHTML = "";
        selectedFiles.forEach(file => {
            const li = document.createElement("li");
            li.textContent = file.name;
            fileList.appendChild(li);
        });

        if (selectedFiles.length > 0) {
            uploadBtn.classList.add("active");
            uploadBtn.disabled = false;
        } else {
            uploadBtn.classList.remove("active");
            uploadBtn.disabled = true;
        }
    });

    /* ============================
       UPLOAD FILE
    ============================ */
    uploadBtn.addEventListener("click", () => {
        if (selectedFiles.length === 0) return;
        uploadSequentially(selectedFiles);
    });

    async function uploadSequentially(files) {
        uploadBtn.disabled = true;

        fileList.innerHTML = ""; // Kosongkan list → tampilkan progress

        for (let file of files) {
            const fileBox = document.createElement("li");
            fileBox.innerHTML = `
                <strong>${file.name}</strong>
                <div class="progress">
                    <div class="progress-bar"></div>
                </div>
                <span class="status">Mengupload...</span>
            `;
            fileList.appendChild(fileBox);

            await uploadSingleFile(file, fileBox);
        }

        uploadBtn.disabled = false;
    }

    async function uploadSingleFile(file, box) {

        const bar = box.querySelector(".progress-bar");
        const status = box.querySelector(".status");

        const fd = new FormData();
        fd.append("files", file);

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: fd
            });

            if (res.ok) {
                bar.style.width = "100%";
                bar.classList.add("success");
                status.textContent = "Selesai ✅";
                status.classList.add("success");
            } else {
                bar.classList.add("error");
                status.textContent = "Gagal ❌";
                status.classList.add("error");
            }
        } catch (e) {
            bar.classList.add("error");
            status.textContent = "Gagal ❌";
            status.classList.add("error");
        }
    }

});