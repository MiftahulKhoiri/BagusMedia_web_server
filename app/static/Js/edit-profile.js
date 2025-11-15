// ============================================
//  PREVIEW FOTO SAAT USER UPLOAD
// ============================================
const uploadInput = document.getElementById("upload-photo");
const previewPhoto = document.getElementById("preview-photo");

if (uploadInput) {
    uploadInput.addEventListener("change", () => {
        const file = uploadInput.files[0];
        if (file) {
            // Tampilkan preview foto
            previewPhoto.src = URL.createObjectURL(file);
        }
    });
}


// ============================================
//  FUNGSI UPLOAD FOTO KE SERVER
// ============================================
async function uploadPhoto() {
    const file = uploadInput.files[0];
    if (!file) return null;   // Jika foto tidak diganti

    const formData = new FormData();
    formData.append("photo", file);

    const res = await fetch("/api/upload-photo", {
        method: "POST",
        body: formData
    });

    const result = await res.json();

    if (result.status === "success") {
        return result.foto;   // path foto baru
    } else {
        alert("Gagal upload foto!");
        return null;
    }
}


// ============================================
//  TOMBOL SIMPAN PROFIL
// ============================================
const saveBtn = document.getElementById("save-btn");

if (saveBtn) {
    saveBtn.addEventListener("click", async () => {

        saveBtn.disabled = true;
        saveBtn.innerText = "Menyimpan...";

        // Ambil input data user
        const nama  = document.getElementById("edit-nama").value;
        const email = document.getElementById("edit-email").value;
        const jk    = document.getElementById("edit-jk").value;
        const umur  = document.getElementById("edit-umur").value;
        const bio   = document.getElementById("edit-bio").value;

        // Upload foto terlebih dahulu
        const fotoPath = await uploadPhoto();

        // Buat object data profil
        const data = {
            nama,
            email,
            jk,
            umur,
            bio,
        };

        // Jika foto diubah → masukkan path foto baru
        if (fotoPath) {
            data.foto = fotoPath;
        }

        // Kirim data ke server
        const res = await fetch("/api/save-profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (result.status === "success") {
            alert("Profil berhasil diperbarui!");

            // Kembali ke halaman profil
            window.location.href = "/profile";
        } else {
            alert("Gagal menyimpan profil!");
        }

        saveBtn.disabled = false;
        saveBtn.innerText = "Simpan";
    });
}


// ============================================
//  ANIMASI NEON UNTUK INPUT & TOMBOL
// ============================================
document.querySelectorAll("input, textarea, select").forEach(el => {
    el.addEventListener("focus", () => {
        el.style.boxShadow = "0 0 12px cyan";
        el.style.borderColor = "cyan";
    });

    el.addEventListener("blur", () => {
        el.style.boxShadow = "none";
        el.style.borderColor = "cyan";
    });
});

console.log("edit-profile.js loaded — Ready!");