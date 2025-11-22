/* =============================== */
/*       SIDEBAR DRAG RESIZE      */
/* =============================== */
const sidebar = document.getElementById("sidebar");
const dragbar = document.getElementById("dragbar");
const toggleBtn = document.getElementById("toggleSidebar");

let dragging = false;

/* Desktop drag */
dragbar.addEventListener("mousedown", () => {
    dragging = true;
    dragbar.classList.add("active");
});

document.addEventListener("mousemove", (e) => {
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
    dragging = true;
    dragbar.classList.add("active");
});

document.addEventListener("touchmove", (e) => {
    if (!dragging) return;

    let newWidth = e.touches[0].clientX;
    if (newWidth < 150) newWidth = 150;
    if (newWidth > 400) newWidth = 400;

    sidebar.style.width = newWidth + "px";
});

document.addEventListener("touchend", () => {
    dragging = false;
    dragbar.classList.remove("active");
});


/* =============================== */
/*       TOGGLE SIDEBAR           */
/* =============================== */
toggleBtn.addEventListener("click", () => {
    if (sidebar.style.width === "0px") {
        sidebar.style.width = "260px";
        dragbar.style.display = "block";
    } else {
        sidebar.style.width = "0px";
        dragbar.style.display = "none";
    }
});


/* =============================== */
/*  SISTEM FILE — FOLDER & FILE   */
/* =============================== */

function switchRoot(folder) {
    console.log("Switch root:", folder);
}

function goUp() {
    console.log("Up folder");
}

function createFolder() {
    console.log("Create Folder");
}

function renameCurrentFolder() {
    console.log("Rename Folder");
}

function deleteCurrentFolder() {
    console.log("Delete Folder");
}

function uploadFiles() {
    console.log("Uploading...");
}