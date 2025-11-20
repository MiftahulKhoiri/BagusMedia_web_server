// =====================================================
// FILE MANAGER – BAGUS MEDIA SERVER (CLEAN VERSION)
// =====================================================

// Elemen UI
const sortSelect = document.getElementById("sort");
const searchInput = document.getElementById("search");
const fileList = document.getElementById("file-list");

const modal = document.getElementById("modal-rename");
const modalInput = document.getElementById("rename-input");
const renameCancel = document.getElementById("rename-cancel");
const renameSave = document.getElementById("rename-save");

const miniPlayer = document.getElementById("mini-player");
const miniMediaArea = document.getElementById("mini-media-area");
const miniClose = document.getElementById("mini-close");

let renameTarget = null;
let currentFiles = [];

// =====================================================
// FETCH FILE LIST + ADAPTER
// =====================================================

async function loadFiles() {
    const res = await fetch("/api/filemanager/list");
    const data = await res.json();

    // Adapt API → Format yang dipakai frontend
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
    const sortType = sortSelect.value;

    // Filtering
    let result = files.filter(f =>
        f.name.toLowerCase().includes(searchText)
    );

    // Sorting
    if (sortType === "name") {
        result.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortType === "size") {
        result.sort((a, b) => a.size - b.size);
    } else if (sortType === "date") {
        result.sort((a, b) => new Date(b.mtime) - new Date(a.mtime));
    }

    // Render HTML
    fileList.innerHTML = result.map(file => `
        <div class="fm-card">
            <div class="fm-thumb">${getThumbnail(file)}</div>

            <div class="fm-title">${file.name}</div>

            <div class="fm-meta">
                ${formatSize(file.size)} • ${formatDate(file.mtime)}
            </div>

            <div class="fm-actions">
                <button onclick="previewFile('${file.url}', '${file.type}')">▶ Play</button>
                <button onclick="downloadFile('${file.url}')">⬇ Download</button>
                <button onclick="openRename('${file.name}')">✏ Rename</button>
                <button onclick="deleteFile('${file.name}')">🗑 Hapus</button>
            </div>
        </div>
    `).join("");
}

// =====================================================
// THUMBNAIL
// =====================================================

function getThumbnail(file) {
    switch (file.type) {
        case "image": return `<img src="${file.url}">`;
        case "audio": return "🎵";
        case "video": return "🎬";
        default: return "📄";
    }
}

// =====================================================
// FORMAT UTILITIES
// =====================================================

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(ts) {
    return new Date(ts).toLocaleString("id-ID");
}

// =====================================================
// PREVIEW (MINI PLAYER)
// =====================================================

function previewFile(url, type) {
    miniPlayer.classList.remove("hidden");

    if (type === "audio") {
        miniMediaArea.innerHTML = `<audio controls autoplay src="${url}"></audio>`;
    } else if (type === "video") {
        miniMediaArea.innerHTML = `<video controls autoplay src="${url}"></video>`;
    } else {
        miniMediaArea.innerHTML = `<p>Preview tidak tersedia</p>`;
    }
}

miniClose.onclick = () => {
    miniPlayer.classList.add("hidden");
    miniMediaArea.innerHTML = "";
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
// RENAME
// =====================================================

function openRename(name) {
    renameTarget = name;
    modalInput.value = name;
    modal.classList.remove("hidden");
}

renameCancel.onclick = () => modal.classList.add("hidden");

renameSave.onclick = async () => {
    const newName = modalInput.value.trim();
    if (!newName) return;

    await fetch("/api/filemanager/rename", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ old_name: renameTarget, new_name: newName })
    });

    modal.classList.add("hidden");
    loadFiles();
};

// =====================================================
// DELETE
// =====================================================

async function deleteFile(name) {
    if (!confirm(`Hapus file: ${name}?`)) return;

    await fetch("/api/filemanager/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: name })
    });

    loadFiles();
}

// =====================================================
// EVENT HANDLER
// =====================================================

searchInput.oninput = loadFiles;
sortSelect.onchange = loadFiles;

// =====================================================
// INITIAL LOAD
// =====================================================

loadFiles();