// Ambil elemen yang dibutuhkan
const fileInput = document.getElementById('file-input');
const uploadArea = document.getElementById('upload-area');
const progressContainer = document.getElementById('upload-progress');

// Ketika area di-klik, buka file picker
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Ketika file dipilih
fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    if (files.length > 0) {
        uploadSequentially(files);
    }
});

// Fungsi utama upload berurutan
async function uploadSequentially(files) {
    progressContainer.innerHTML = ''; // Kosongkan progress sebelumnya

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const progressItem = document.createElement('div');
        progressItem.classList.add('progress-item');

        progressItem.innerHTML = `
            <div class="progress-info">
                <span>${file.name}</span>
                <span class="status">Menunggu...</span>
            </div>
            <div class="progress-bar"><div class="progress-fill"></div></div>
        `;

        progressContainer.appendChild(progressItem);

        // 🔵 Tambahkan class aktif agar efek "bernapas" muncul
        progressItem.classList.add('active');

        // Jalankan upload
        await uploadSingleFile(file, progressItem);

        // 🔵 Setelah selesai upload, hapus efek aktif
        progressItem.classList.remove('active');
    }
}

// Fungsi upload satu file
async function uploadSingleFile(file, progressItem) {
    const progressFill = progressItem.querySelector('.progress-fill');
    const statusText = progressItem.querySelector('.status');

    const formData = new FormData();
    formData.append('file', file);

    try {
        statusText.textContent = 'Mengupload...';

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            statusText.textContent = 'Selesai ✅';
            statusText.classList.add('success');
            progressFill.style.width = '100%';
            progressFill.classList.add('success');
        } else {
            statusText.textContent = 'Gagal ❌';
            statusText.classList.add('error');
            progressFill.classList.add('error');
        }
    } catch (error) {
        console.error(error);
        statusText.textContent = 'Gagal ❌';
        statusText.classList.add('error');
        progressFill.classList.add('error');
    }
}