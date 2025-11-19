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