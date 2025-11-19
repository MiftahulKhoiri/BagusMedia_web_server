// ================================
// ADMIN PANEL SCRIPT
// ================================

// Ganti role user
function changeRole(id, role) {
    fetch("/api/change-role", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: id, role: role})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert("❌ " + data.error);
        } else {
            alert("✔ Role pengguna berhasil diubah!");
            location.reload();
        }
    });
}

// Hapus user
function deleteUser(id) {
    if (!confirm("❗ Yakin ingin menghapus user ini?")) return;

    fetch("/api/delete-user", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({user_id: id})
    })
    .then(r => r.json())
    .then(data => {
        if (data.error) {
            alert("❌ " + data.error);
        } else {
            alert("✔ User berhasil dihapus!");
            location.reload();
        }
    });
}

// UPDATE REALTIME SYSTEM MONITOR
async function updateMonitor() {
    try {
        const res = await fetch("/api/monitor");
        const data = await res.json();

        // CPU
        document.getElementById("cpu-bar").style.width = data.cpu + "%";
        document.getElementById("cpu-text").textContent = data.cpu + "%";

        // RAM
        document.getElementById("ram-bar").style.width = data.ram_percent + "%";
        document.getElementById("ram-text").textContent =
            `${data.ram_used} / ${data.ram_total} GB (${data.ram_percent}%)`;

        // DISK
        document.getElementById("disk-bar").style.width = data.disk_percent + "%";
        document.getElementById("disk-text").textContent =
            `${data.disk_used} / ${data.disk_total} GB (${data.disk_percent}%)`;

    } catch (err) {
        console.log("Monitor error:", err);
    }
}

// refresh tiap 1 detik
setInterval(updateMonitor, 1000);
updateMonitor();