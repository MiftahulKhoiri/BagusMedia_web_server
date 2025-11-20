// =====================================================
// FILE MANAGER – BAGUS MEDIA SERVER (FIXED VERSION)
// =====================================================

// Elemen UI
const searchInput = document.getElementById("search");
const fileList = document.getElementById("fm-list");   // FIXED

// Tidak ada sort select di HTML, jadi kita matikan fitur sort
let currentFiles = [];

// =====================================================
// FETCH FILE LIST (API BENAR)
// =====================================================

async function loadFiles() {
    const res = await fetch("/api/files");   // FIXED URL
    const data = await res.json();

    currentFiles = data.files.map(f => ({
        name: f.name,
        size: f.size_bytes,
        mtime: f.mtime,
        url: f.download_url,
        type: f.is_audio ? "audio" : f.is_video ? "video" : "other"
    }));

    renderFiles(currentFiles);
}

// =====================================================
// RENDER FILE LIST
// =====================================================

function renderFiles(files) {
    const searchText = searchInput.value.toLowerCase();

    let result = files.filter(f =>
        f.name.toLowerCase().includes(searchText)
    );

    fileList.innerHTML = result.map(file => `
        <div class="fm-card">
            <div class="fm-thumb">${getThumbnail(file)}</div>

            <div class="fm-title">${file.name}</div>

            <div class="fm-meta">
                ${formatSize(file.size)} • ${file.mtime}
            </div>

            <div class="fm-actions">
                <button onclick="previewFile('${file.url}', '${file.type}')">▶ Play</button>
                <button onclick="downloadFile('${file.url}')">⬇ Download</button>
            </div>
        </div>
    `).join("");
}

// =====================================================
// THUMBNAIL
// =====================================================

function getThumbnail(file) {
    if (file.type === "audio") return "🎵";
    if (file.type === "video") return "🎬";
    return "📄";
}

// =====================================================
// FORMAT UTILITIES
// =====================================================

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// =====================================================
// MINI PLAYER
// =====================================================

function previewFile(url, type) {
    const miniPlayer = document.getElementById("mini-player");
    const miniMediaArea = document.getElementById("mini-media-area");

    miniPlayer.classList.remove("hidden");

    if (type === "audio") {
        miniMediaArea.innerHTML = `<audio controls autoplay src="${url}"></audio>`;
    } else if (type === "video") {
        miniMediaArea.innerHTML = `<video controls autoplay src="${url}"></video>`;
    } else {
        miniMediaArea.innerHTML = `<p>Preview tidak tersedia</p>`;
    }
}

document.getElementById("mini-close").onclick = () => {
    document.getElementById("mini-player").classList.add("hidden");
    document.getElementById("mini-media-area").innerHTML = "";
};

// =====================================================
// DOWNLOAD
// =====================================================

function downloadFile(url) {
    const a = document.createElement("a");
    a.href = url;
    a.download = url.split("/").pop();
    a.click();
}

// =====================================================
// EVENT HANDLER
// =====================================================

searchInput.oninput = loadFiles;

// =====================================================
// INITIAL LOAD
// =====================================================

loadFiles();