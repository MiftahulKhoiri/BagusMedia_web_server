// =====================================================
// FILE MANAGER – BAGUS MEDIA SERVER
// =====================================================

// Elemen penting
const sortSelect = document.getElementById("sort");
const searchInput = document.getElementById("search");
const fileList = document.getElementById("file-list");

const modal = document.getElementById("modal-rename");
const modalInput = document.getElementById("rename-input");
const renameCancel = document.getElementById("rename-cancel");
const renameSave = document.getElementById("rename-save");

let renameTarget = null;

// Mini Player
const miniPlayer = document.getElementById("mini-player");
const miniMediaArea = document.getElementById("mini-media-area");
const miniClose = document.getElementById("mini-close");

// =====================================================
// FETCH FILE LIST (AJAX)
// =====================================================

async function loadFiles() {
    const res = await fetch("/api/filemanager/list");
    const data = await res.json();
    renderFiles(data.files);
    return data.files;
}

// =====================================================
// RENDER FILE LIST
// =====================================================

let currentFiles = [];

function renderFiles(files) {
    currentFiles = files;

    const searchText = searchInput.value.toLowerCase();
    const sortType = sortSelect.value;

    // Filter
    let filtered = files.filter(f => f.name.toLowerCase().includes(searchText));

    // Sorting
    if (sortType === "name") {
        filtered.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortType === "size") {
        filtered.sort((a, b) => a.size - b.size);
    } else if (sortType === "date") {
        filtered.sort((a, b) => new Date(b.mtime) - new Date(a.mtime));
    }

    // Render
    fileList.innerHTML = "";

    filtered.forEach(file => {
        const card = document.createElement("div");
        card.className = "fm-card";

        const thumb = getThumbnail(file);

        card.innerHTML = `
            <div class="fm-thumb">${thumb}</div>
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
        `;

        fileList.appendChild(card);
    });
}

// =====================================================
// GENERATE THUMBNAIL
// =====================================================

function getThumbnail(file) {
    if (file.type === "image") {
        return `<img src="${file.url}">`;
    }
    if (file.type === "audio") return "🎵";
    if (file.type === "video") return "🎬";
    return "📄";
}

// =====================================================
// FORMAT BANTUAN
// =====================================================

function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function formatDate(ts) {
    return new Date(ts).toLocaleString("id-ID");
}

// =====================================================
// PREVIEW / MINI PLAYER
// =====================================================

function previewFile(url, type) {
    miniPlayer.classList.remove("hidden");
    miniMediaArea.innerHTML = "";

    if (type === "audio") {
        miniMediaArea.innerHTML = `<audio controls autoplay src="${url}"></audio>`;
    } 
    else if (type === "video") {
        miniMediaArea.innerHTML = `<video controls autoplay src="${url}"></video>`;
    } 
    else {
        miniMediaArea.innerHTML = `<p>Preview tidak tersedia</p>`;
    }
}

miniClose.onclick = () => {
    miniPlayer.classList.add("hidden");
    miniMediaArea.innerHTML = "";
};

// =====================================================
// DOWNLOAD FILE
// =====================================================

function downloadFile(url) {
    const a = document.createElement("a");
    a.href = url;
    a.download = url.split("/").pop();
    a.click();
}

// =====================================================
// RENAME FILE (OPEN MODAL)
// =====================================================

function openRename(name) {
    renameTarget = name;
    modalInput.value = name;
    modal.classList.remove("hidden");
}

renameCancel.onclick = () => {
    modal.classList.add("hidden");
};

renameSave.onclick = async () => {
    const newName = modalInput.value.trim();
    if (!newName) return;

    const res = await fetch("/api/filemanager/rename", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ old_name: renameTarget, new_name: newName })
    });

    modal.classList.add("hidden");
    await loadFiles();
};

// =====================================================
// DELETE FILE
// =====================================================

async function deleteFile(name) {
    if (!confirm("Hapus file: " + name + " ?")) return;

    await fetch("/api/filemanager/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: name })
    });

    await loadFiles();
}

// =====================================================
// EVENT LISTENER
// =====================================================

sortSelect.onchange = loadFiles;
searchInput.oninput = loadFiles;

// =====================================================
// INITIAL LOAD
// =====================================================

loadFiles();