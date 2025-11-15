document.addEventListener("DOMContentLoaded", () => {

    const coverPhoto = document.getElementById("cover-photo");
    const coverInput = document.getElementById("cover-input");

    const profilePhoto = document.getElementById("profile-photo");
    const profileInput = document.getElementById("photo-input");

    /* ======================================
       GANTI COVER FOTO LANGSUNG DI PROFIL
    ====================================== */
    coverPhoto.addEventListener("click", () => coverInput.click());

    coverInput.addEventListener("change", async () => {
        const file = coverInput.files[0];
        if (!file) return;

        const fd = new FormData();
        fd.append("photo", file);
        fd.append("type", "cover");

        const res = await fetch("/api/upload-photo", {
            method: "POST",
            body: fd
        });

        const result = await res.json();
        if (result.status === "success") {
            coverPhoto.src = `/static/profile/${result.foto}?t=${Date.now()}`;
            alert("Cover berhasil diperbarui!");
        } else {
            alert("Gagal upload cover!");
        }
    });

    /* ======================================
       GANTI FOTO PROFIL LANGSUNG DI PROFIL
    ====================================== */
    profilePhoto.addEventListener("click", () => profileInput.click());

    profileInput.addEventListener("change", async () => {
        const file = profileInput.files[0];
        if (!file) return;

        const fd = new FormData();
        fd.append("photo", file);
        fd.append("type", "profile");

        const res = await fetch("/api/upload-photo", {
            method: "POST",
            body: fd
        });

        const result = await res.json();
        if (result.status === "success") {
            profilePhoto.src = `/static/profile/${result.foto}?t=${Date.now()}`;
            alert("Foto profil berhasil diperbarui!");
        } else {
            alert("Gagal upload foto profil!");
        }
    });

});