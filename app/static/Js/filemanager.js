/* Neon Android-style File Manager JS
   Terhubung penuh ke API Flask yang kamu kirim.
*/

(function(){
  // state
  let currentRoot = "mp3";
  let currentPath = "";
  let viewMode = "grid"; // or "list"

  // elements
  const drawer = document.getElementById("drawer");
  const backdrop = document.getElementById("drawerBackdrop");
  const openDrawerBtn = document.getElementById("openDrawer");
  const closeDrawerBtn = document.getElementById("closeDrawer");
  const drawerItems = document.querySelectorAll(".drawer-item");
  const filelistEl = document.getElementById("filelist");
  const pathDisplay = document.getElementById("pathDisplay");
  const breadcrumb = document.getElementById("breadcrumb");
  const toggleViewBtn = document.getElementById("toggleView");
  const fileInput = document.getElementById("fileInput");
  const fabNew = document.getElementById("fabNew");
  const btnUp = document.getElementById("btnUp");
  const btnNew = document.getElementById("btnNew");
  const btnRename = document.getElementById("btnRename");
  const btnDelete = document.getElementById("btnDelete");
  const toastEl = document.getElementById("toast");

  // helpers
  function toast(msg, time=1600){
    toastEl.textContent = msg;
    toastEl.classList.remove("hidden");
    setTimeout(()=> toastEl.classList.add("hidden"), time);
  }

  function qs(id){ return document.getElementById(id) }

  // DRAWER control
  function openDrawer(){ drawer.classList.add("open"); backdrop.classList.remove("hidden"); }
  function closeDrawer(){ drawer.classList.remove("open"); backdrop.classList.add("hidden"); }
  openDrawerBtn.addEventListener("click", openDrawer);
  closeDrawerBtn.addEventListener("click", closeDrawer);
  backdrop.addEventListener("click", closeDrawer);

  // swipe gesture for drawer (simple)
  let startX = null;
  window.addEventListener("touchstart", (e)=> startX = e.touches[0].clientX );
  window.addEventListener("touchmove", (e)=>{
    if (startX===null) return;
    let dx = e.touches[0].clientX - startX;
    // swipe right from left edge to open
    if (startX < 30 && dx > 60) openDrawer();
    // swipe left to close if drawer open
    if (drawer.classList.contains("open") && dx < -30) closeDrawer();
  });
  window.addEventListener("touchend", ()=> startX = null);

  // drawer items click -> switch root
  drawerItems.forEach(it=>{
    it.addEventListener("click", ()=> {
      const root = it.dataset.root;
      currentRoot = root;
      currentPath = "";
      closeDrawer();
      loadFiles();
    });
  });

  // Toggle view
  toggleViewBtn.addEventListener("click", ()=>{
    viewMode = (viewMode === "grid") ? "list" : "grid";
    renderFiles(lastData);
  });

  // top controls
  btnUp.addEventListener("click", ()=>{
    if (!currentPath) return toast("Sudah di root");
    currentPath = currentPath.split("/").slice(0,-1).join("/");
    loadFiles();
  });
  btnNew.addEventListener("click", createFolderPrompt);
  fabNew.addEventListener("click", createFolderPrompt);
  btnRename.addEventListener("click", renameCurrentFolderPrompt);
  btnDelete.addEventListener("click", deleteCurrentFolderPrompt);

  // upload
  fileInput.addEventListener("change", uploadFiles);

  // drag & drop upload in filearea
  const filearea = document.getElementById("filearea");
  filearea.addEventListener("dragover", e=> { e.preventDefault(); filearea.style.opacity = 0.92; });
  filearea.addEventListener("dragleave", e=> { filearea.style.opacity = 1; });
  filearea.addEventListener("drop", e=>{
    e.preventDefault();
    filearea.style.opacity = 1;
    const dt = e.dataTransfer;
    if (!dt || !dt.files) return;
    const files = dt.files;
    uploadFileList(files);
  });

  // fetch & render
  let lastData = {folders:[], files:[]};
  async function loadFiles(){
    try{
      showLoading(true);
      const url = `/filemanager/api/files?root=${encodeURIComponent(currentRoot)}&path=${encodeURIComponent(currentPath)}`;
      const res = await fetch(url);
      if (!res.ok) { toast("Gagal memuat"); showLoading(false); return; }
      const data = await res.json();
      lastData = data;
      renderFiles(data);
      updatePathUi();
      showLoading(false);
    }catch(err){
      console.error(err);
      toast("Error jaringan");
      showLoading(false);
    }
  }

  function showLoading(flag){
    if(flag) filelistEl.innerHTML = `<div style="padding:20px;text-align:center;color:var(--muted)">Memuat...</div>`;
  }

  function updatePathUi(){
    const display = currentPath || "/";
    pathDisplay.textContent = `${currentRoot} / ${display}`;
    breadcrumb.textContent = display === "/" ? "/" : display;
  }

  // render routine
  function renderFiles(data){
    filelistEl.className = (viewMode === "grid") ? "grid" : "list";
    filelistEl.innerHTML = "";

    // folders first
    data.folders.forEach(f=>{
      const el = document.createElement("div");
      el.className = "tile";
      el.innerHTML = `
        <div class="thumb">📁</div>
        <div class="meta">
          <div class="name">${escapeHtml(f.name)}</div>
          <div class="metainfo">${f.mtime} • folder</div>
        </div>
        <div class="actions">
          <button class="btn" data-name="${escapeHtml(f.name)}" onclick="window.openFolderFromUI('${escapeForJS(f.name)}')">Open</button>
          <button class="btn btn-danger" onclick="window.deleteFolderFromUI('${escapeForJS(f.name)}')">Hapus</button>
        </div>
      `;
      filelistEl.appendChild(el);
    });

    // files
    data.files.forEach(file=>{
      const el = document.createElement("div");
      el.className = "tile";
      const thumbHtml = file.thumbnail ? `<div class="thumb" style="background-image:url('${file.thumbnail}';background-size:cover;background-position:center)"></div>` : `<div class="thumb">${getIconForFile(file.name)}</div>`;
      el.innerHTML = `
        ${thumbHtml}
        <div class="meta">
          <div class="name">${escapeHtml(file.name)}</div>
          <div class="metainfo">${file.size} • ${file.mtime}</div>
        </div>
        <div class="actions">
          <a class="btn" href="${file.download_url}">⬇</a>
          <button class="btn btn-danger" onclick="window.deleteFileFromUI('${escapeForJS(file.name)}')">Hapus</button>
        </div>
      `;
      filelistEl.appendChild(el);
    });
  }

  // utility: small escaping helpers
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])) }
  function escapeForJS(s){ return String(s).replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/"/g,'\\"') }

  // icons by extension
  function getIconForFile(name){
    const ext = name.split('.').pop().toLowerCase();
    if (['mp3','wav','aac'].includes(ext)) return '🎵';
    if (['mp4','mkv','webm'].includes(ext)) return '🎬';
    if (['jpg','jpeg','png','gif','webp'].includes(ext)) return '🖼';
    if (['pdf'].includes(ext)) return '📕';
    if (['zip','rar','7z'].includes(ext)) return '🗜';
    return '📄';
  }

  // CRUD actions (call API)
  async function createFolderPrompt(){
    const name = prompt("Nama folder baru:");
    if (!name) return;
    try{
      const res = await fetch("/filemanager/api/create-folder", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ root: currentRoot, path: currentPath, name: name })
      });
      const j = await res.json();
      if (j.error) return toast(j.error);
      toast("Folder dibuat");
      loadFiles();
    }catch(e){ toast("Gagal membuat") }
  }

  async function deleteFolderPrompt(){
    const name = prompt("Masukkan nama folder yang ingin dihapus:");
    if (!name) return;
    if (!confirm(`Hapus folder '${name}'?`)) return;
    try{
      const res = await fetch("/filemanager/api/delete-folder", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ root: currentRoot, path: currentPath, foldername: name })
      });
      const j = await res.json();
      if (j.error) return toast(j.error);
      toast("Folder dihapus");
      loadFiles();
    }catch(e){ toast("Gagal") }
  }

  async function deleteCurrentFolderPrompt(){
    if (!currentPath) return toast("Tidak bisa hapus root");
    const parts = currentPath.split("/");
    const name = parts.pop();
    if (!confirm(`Hapus folder '${name}'?`)) return;
    try{
      const res = await fetch("/filemanager/api/delete-folder", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ root: currentRoot, path: parts.join("/"), foldername: name })
      });
      const j = await res.json();
      if (j.error) return toast(j.error);
      currentPath = parts.join("/");
      toast("Folder dihapus");
      loadFiles();
    }catch(e){ toast("Gagal") }
  }

  async function renameCurrentFolderPrompt(){
    if (!currentPath) return toast("Tidak bisa rename root");
    const parts = currentPath.split("/");
    const oldName = parts.pop();
    const newName = prompt("Nama baru:", oldName);
    if (!newName) return;
    try{
      const res = await fetch("/filemanager/api/rename-folder", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ root: currentRoot, path: parts.join("/"), old_name: oldName, new_name: newName })
      });
      const j = await res.json();
      if (j.error) return toast(j.error);
      parts.push(j.new_name || newName);
      currentPath = parts.join("/");
      toast("Folder diganti");
      loadFiles();
    }catch(e){ toast("Gagal") }
  }

  // delete file
  async function deleteFileByName(name){
    if (!confirm(`Hapus file ${name}?`)) return;
    try{
      const res = await fetch("/filemanager/api/delete-file", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ root: currentRoot, path: currentPath, filename: name })
      });
      const j = await res.json();
      if (j.error) return toast(j.error);
      toast("File dihapus");
      loadFiles();
    }catch(e){ toast("Gagal") }
  }

  // upload
  async function uploadFiles(){
    const files = fileInput.files;
    if (!files || files.length===0) return;
    uploadFileList(files);
  }

  async function uploadFileList(filesLike){
    const form = new FormData();
    for (const f of filesLike) form.append("files", f);
    try{
      const res = await fetch(`/filemanager/api/upload?root=${encodeURIComponent(currentRoot)}&path=${encodeURIComponent(currentPath)}`, {
        method:"POST", body: form
      });
      const j = await res.json();
      if (j.results){
        toast("Upload selesai");
        loadFiles();
      } else if (j.error) {
        toast(j.error);
      } else {
        toast("Selesai");
        loadFiles();
      }
    }catch(e){ toast("Gagal upload"); console.error(e) }
  }

  // open folder helper (exposed to inline onclick)
  window.openFolderFromUI = function(name){
    currentPath = (currentPath ? currentPath + "/" + name : name);
    loadFiles();
  };

  window.deleteFolderFromUI = function(name){
    if (!confirm(`Hapus folder ${name}?`)) return;
    fetch("/filemanager/api/delete-folder", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ root: currentRoot, path: currentPath, foldername: name })
    }).then(r=>r.json()).then(j=>{
      if (j.error) toast(j.error); else { toast("Folder dihapus"); loadFiles(); }
    }).catch(()=>toast("Gagal"));
  };

  window.deleteFileFromUI = function(name){
    deleteFileByName(name);
  };

  // open file (download handled by link), but we could preview — left simple

  // initial load
  loadFiles();

  // expose some actions to top-level buttons
  window.createFolderPrompt = createFolderPrompt;
  window.renameCurrentFolderPrompt = renameCurrentFolderPrompt;
  window.deleteCurrentFolderPrompt = deleteCurrentFolderPrompt;
})();