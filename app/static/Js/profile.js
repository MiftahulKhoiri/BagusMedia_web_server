// ================================
//  UTIL: POPUP NOTIF
// ================================
function notif(msg, type = "success") {
    alert((type === "error" ? "⚠ " : "✔ ") + msg);
}


// ================================
//  PREVIEW FOTO PROFIL / COVER
// ================================
function previewImage(input, targetId) {
    const file = input.files[0];
    if (!file) return;

    // Validasi file
    if (!file.type.startsWith("image/")) {
        notif("Hanya file gambar yang diperbolehkan!", "error");
        return;
    }

    const img = document.getElementById(targetId);
    img.src = URL.createObjectURL(file);
    img.style.opacity = "0.5";

    setTimeout(() => {
        img.style.opacity = "1";
    }, 150);
}


// ================================
//  UPLOAD FOTO (PROFILE / COVER)
// ================================
async function uploadPhoto(input, type) {
    const file = input.files[0];
    if (!file) return;

    let form = new FormData();
    form.append("photo", file);
    form.append("type", type);

    try {
        const res = await fetch("/api/upload-photo", {
            method: "POST",
            body: form
        });

        const data = await res.json();

        if (data.status === "success") {
            notif("Foto berhasil diperbarui!");
        } else {
            notif("Gagal upload foto!", "error");
        }

    } catch (err) {
        notif("Kesalahan koneksi!", "error");
    }
}


// ================================
//  SIMPAN DATA PROFIL
// ================================
async function saveProfile() {
    const data = {
        nama: document.getElementById("nama").value,
        email: document.getElementById("email").value,
        jk: document.getElementById("jk").value,
        umur: document.getElementById("umur").value,
        bio: document.getElementById("bio").value
    };

    try {
        const res = await fetch("/api/save-profile", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (result.status === "success") {
            notif("Profil berhasil disimpan!");
        } else {
            notif("Gagal menyimpan profil!", "error");
        }

    } catch (err) {
        notif("Kesalahan koneksi!", "error");
    }
}