/* ===== File: filemanager.js ===== */

let currentRoot = "mp3";
let currentPath = "";

// Switch Root Folder
function switchRoot(root) {
  currentRoot = root;
  currentPath = "";
  loadFiles();
}

// Load File List
function loadFiles() {
  fetch(`/api/files?root=${currentRoot}&path=${currentPath}`)
    .then(r => r.json())
    .then(data => render(data))
    .catch(err => console.error("Load error:", err));
}

// Render UI
function render(data) {
  document.getElementById("pathDisplay").innerText = `${currentRoot}/${currentPath}`;
  let html = "";

  // Folders
  data.folders.forEach(f => {
    html += `
      <div class='item'>
        <span class='folder' onclick='openFolder("${f.name}")'>📁 ${f.name}</span>
        <span>
          <button onclick='renameFolder("${f.name}")'>✏</button>
          <button onclick='deleteFolder("${f.name}")'>🗑</button>
        </span>
      </div>`;
  });

  // Files
  data.files.forEach(f => {
    let preview = "";
    if (f.is_video) preview = `<video controls src='${f.path}'></video>`;
    if (f.is_audio) preview = `<audio controls src='${f.path}'></audio>`;

    html += `
      <div class='item'>
        <div>
          📄 ${f.name}
          ${preview ? `<div class='preview-box'>${preview}</div>` : ""}
        </div>
        <span>
          <button onclick='renameFile("${f.name}")'>✏ Rename</button>
          <button onclick='deleteFile("${f.name}")'>🗑 Delete</button>
          <a href='${f.download_url}'><button>⬇ Download</button></a>
        </span>
      </div>`;
  });

  document.getElementById("filelist").innerHTML = html;
}

// Open Folder
function openFolder(name) {
  currentPath = (currentPath + "/" + name).replace(/^\/+/, "");
  loadFiles();
}

// Go Up One Level
function goUp() {
  if (!currentPath) return;
  let parts = currentPath.split("/");
  parts.pop();
  currentPath = parts.join("/");
  loadFiles();
}

// Create Folder
function createFolder() {
  let name = prompt("Folder baru?");
  if (!name) return;
  fetch(`/api/create-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: currentPath, name })
  }).then(() => loadFiles());
}

// Delete Folder
function deleteFolder(foldername) {
  if (!confirm("Hapus folder beserta isinya?")) return;
  fetch(`/api/delete-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: currentPath, foldername })
  }).then(() => loadFiles());
}

// Delete CURRENT folder
function deleteCurrentFolder() {
  if (!currentPath) return alert("Tidak bisa hapus root!");

  let parts = currentPath.split("/");
  let foldername = parts.pop();
  let parent = parts.join("/");

  if (!confirm(`Hapus folder ${foldername}?`)) return;

  fetch(`/api/delete-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: parent, foldername })
  }).then(() => {
    currentPath = parent;
    loadFiles();
  });
}

// Rename folder
function renameFolder(old_name) {
  let new_name = prompt("Nama baru?", old_name);
  if (!new_name) return;

  fetch(`/api/rename-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: currentPath, old_name, new_name })
  }).then(() => loadFiles());
}

// Rename current folder
function renameCurrentFolder() {
  if (!currentPath) return alert("Root tidak bisa di-rename!");

  let parts = currentPath.split("/");
  let old_name = parts.pop();
  let parent = parts.join("/");
  let new_name = prompt("Nama baru?", old_name);
  if (!new_name) return;

  fetch(`/api/rename-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: parent, old_name, new_name })
  }).then(() => {
    currentPath = (parent + "/" + new_name).replace(/^\/+/, "");
    loadFiles();
  });
}

// Delete File
function deleteFile(filename) {
  if (!confirm("Hapus file ini?")) return;
  fetch(`/api/delete-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: currentPath, filename })
  }).then(() => loadFiles());
}

// Rename File
function renameFile(old_name) {
  let new_name = prompt("Nama baru?", old_name);
  if (!new_name) return;

  fetch(`/api/rename-file`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ root: currentRoot, path: currentPath, old_name, new_name })
  }).then(() => loadFiles());
}

// Upload Files
function uploadFiles() {
  let files = document.getElementById("fileInput").files;
  let form = new FormData();

  for (let f of files) form.append("files", f);

  fetch(`/api/upload?root=${currentRoot}&path=${currentPath}`, {
    method: "POST",
    body: form
  }).then(() => loadFiles());
}

// INITIAL LOAD
loadFiles();
