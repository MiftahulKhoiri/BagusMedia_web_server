/* ==========================================
   STATE GLOBAL
========================================== */
let currentRoot = "mp3";
let currentPath = "";

/* ==========================================
   LOAD FILE LIST
========================================== */
async function loadFiles() {
    const res = await fetch(`/filemanager/api/files?root=${currentRoot}&path=${currentPath}`);
    const data = await res.json();

    const list = document.getElementById("filelist");
    list.innerHTML = "";

    // FOLDER LIST
    data.folders.forEach(folder => {
        const div = document.createElement("div");
        div.className = "item";
        div.innerHTML = `
            <div class="folder" onclick="openFolder('${folder.name}')">📁 ${folder.name}</div>
            <button class="delete-btn" onclick="deleteFolder('${folder.name}')">🗑</button>
        `;
        list.appendChild(div);
    });

    // FILE LIST
    data.files.forEach(file => {
        const div = document.createElement("div");
        div.className = "item";

        let thumb = "";
        if (file.thumbnail) {
            thumb = `<img src="${file.thumbnail}" style="width:60px;border-radius:6px;margin-right:10px;">`;
        }

        div.innerHTML = `
            <div style="display:flex;align-items:center;gap:12px;">
                ${thumb}
                <div>
                    <div>📄 ${file.name}</div>
                    <small>${file.size} • ${file.mtime}</small>
                </div>
            </div>

            <div style="display:flex;gap:10px;">
                <a href="${file.download_url}" class="btn">⬇</a>
                <button class="btn-danger" onclick="deleteFile('${file.name}')">🗑</button>
            </div>
        `;

        list.appendChild(div);
    });

    updatePathDisplay();
}

/* ==========================================
   SWITCH ROOT
========================================== */
function switchRoot(root) {
    currentRoot = root;
    currentPath = "";
    loadFiles();
}

/* ==========================================
   BUKA FOLDER
========================================== */
function openFolder(folder) {
    currentPath = (currentPath ? currentPath + "/" + folder : folder);
    loadFiles();
}

/* ==========================================
   UP ONE LEVEL
========================================== */
function goUp() {
    if (!currentPath) return;
    currentPath = currentPath.split("/").slice(0, -1).join("/");
    loadFiles();
}

/* ==========================================
   PATH DISPLAY
========================================== */
function updatePathDisplay() {
    const p = currentPath || "/";
    document.getElementById("pathDisplay").innerText = `📁 ${currentRoot} / ${p}`;
}

/* ==========================================
   CREATE FOLDER
========================================== */
async function createFolder() {
    const name = prompt("Nama folder baru:");
    if (!name) return;

    const res = await fetch("/filemanager/api/create-folder", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            root: currentRoot,
            path: currentPath,
            name: name
        })
    });

    const data = await res.json();
    if (data.error) alert(data.error);
    loadFiles();
}

/* ==========================================
   DELETE FOLDER
========================================== */
async function deleteFolder(name) {
    if (!confirm("Hapus folder ini?")) return;

    const res = await fetch("/filemanager/api/delete-folder", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            root: currentRoot,
            path: currentPath,
            foldername: name
        })
    });

    const data = await res.json();
    if (data.error) alert(data.error);
    loadFiles();
}

/* ==========================================
   DELETE FILE
========================================== */
async function deleteFile(name) {
    if (!confirm("Hapus file ini?")) return;

    const res = await fetch("/filemanager/api/delete-file", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            root: currentRoot,
            path: currentPath,
            filename: name
        })
    });

    const data = await res.json();
    if (data.error) alert(data.error);
    loadFiles();
}

/* ==========================================
   RENAME CURRENT FOLDER
========================================== */
async function renameCurrentFolder() {
    if (!currentPath) return alert("Tidak bisa rename root.");

    const oldName = currentPath.split("/").pop();
    const newName = prompt("Nama folder baru:", oldName);
    if (!newName) return;

    const res = await fetch("/filemanager/api/rename-folder", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            root: currentRoot,
            path: currentPath.split("/").slice(0, -1).join("/"),
            old_name: oldName,
            new_name: newName
        })
    });

    const data = await res.json();
    if (data.error) return alert(data.error);

    currentPath = currentPath.split("/").slice(0, -1).concat([data.new_name]).join("/");
    loadFiles();
}

/* ==========================================
   UPLOAD
========================================== */
async function uploadFiles() {
    const input = document.getElementById("fileInput");
    const files = input.files;
    if (!files.length) return;

    const form = new FormData();
    for (let f of files) {
        form.append("files", f);
    }

    const res = await fetch(`/filemanager/api/upload?root=${currentRoot}&path=${currentPath}`, {
        method: "POST",
        body: form
    });

    const data = await res.json();
    console.log("Upload result:", data);
    loadFiles();
}

/* ==========================================
   SIDEBAR DRAGBAR
========================================== */
const sidebar = document.getElementById("sidebar");
const dragbar = document.getElementById("dragbar");
const toggleBtn = document.getElementById("toggleSidebar");
let dragging = false;

/* Desktop drag */
dragbar.addEventListener("mousedown", () => { dragging = true; dragbar.classList.add("active"); });
document.addEventListener("mousemove", e => {
    if (!dragging) return;
    let newWidth = e.clientX;
    if (newWidth < 150) newWidth = 150;
    if (newWidth > 400) newWidth = 400;
    sidebar.style.width = newWidth + "px";
});
document.addEventListener("mouseup", () => {
    dragging = false;
    dragbar.classList.remove("active");
});

/* Mobile drag */
dragbar.addEventListener("touchstart", () => {
    dragging = true; dragbar.classList.add("active");
});
document.addEventListener("touchmove", e => {
    if (!dragging) return;
    let newWidth = e.touches[0].clientX;
    if (newWidth < 150) newWidth = 150;
    if (newWidth > 400) newWidth = 400;
    sidebar.style.width = newWidth + "px";
});
document.addEventListener("touchend", () => {
    dragging = false; dragbar.classList.remove("active");
});

/* Toggle sidebar */
toggleBtn.addEventListener("click", () => {
    if (sidebar.style.width === "0px") {
        sidebar.style.width = "260px";
        dragbar.style.display = "block";
    } else {
        sidebar.style.width = "0px";
        dragbar.style.display = "none";
    }
});

/* Start */
loadFiles();