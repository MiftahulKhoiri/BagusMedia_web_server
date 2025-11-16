document.addEventListener("DOMContentLoaded", () => {

    const coverPhoto = document.getElementById("cover-photo");
    const coverInput = document.getElementById("cover-input");

    const profilePhoto = document.getElementById("profile-photo");
    const profileInput = document.getElementById("photo-input");

    const saveBtn = document.getElementById("save-btn");

    /* ===============================
       GANTI COVER
    =============================== */
    coverPhoto.addEventListener("click", () => coverInput.click());

    coverInput.addEventListener("change", async () => {
        const file = coverInput.files[0];
        if (!file) return;

        const fd = new FormData();
        fd.append("photo", file);
        fd.append("type", "cover");

        const res = await fetch("/api/upload-photo", { method: "POST", body: fd });
        const result = await res.json();

        if (result.status === "success") {
            coverPhoto.src = `/static/profile/${result.foto}?t=${Date.now()}`;
        } else {
            alert("Gagal upload cover!");
        }
    });

    /* ===============================
       GANTI FOTO PROFIL
    =============================== */
    profilePhoto.addEventListener("click", () => profileInput.click());

    profileInput.addEventListener("change", async () => {
        const file = profileInput.files[0];
        if (!file) return;

        const fd = new FormData();
        fd.append("photo", file);
        fd.append("type", "profile");

        const res = await fetch("/api/upload-photo", { method: "POST", body: fd });
        const result = await res.json();

        if (result.status === "success") {
            profilePhoto.src = `/static/profile/${result.foto}?t=${Date.now()}`;
        } else {
            alert("Gagal upload foto profil!");
        }
    });

    /* ===============================
       SIMPAN PROFIL TANPA HILANG FOTO
    =============================== */
    saveBtn.addEventListener("click", async () => {

        const data = {
            nama: document.getElementById("nama").value,
            email: document.getElementById("email").value,
            jk: document.getElementById("jk").value,
            umur: document.getElementById("umur").value,
            bio: document.getElementById("bio").value,

            // simpan nama file foto terbaru
            foto: profilePhoto.src.split("/").pop().split("?")[0],
            cover: coverPhoto.src.split("/").pop().split("?")[0]
        };

        const res = await fetch("/api/save-profile", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (result.status === "success") {
            alert("Profil berhasil diperbarui!");
            window.location.href = "/profile";
        } else {
            alert("Gagal menyimpan profil!");
        }
    });

});