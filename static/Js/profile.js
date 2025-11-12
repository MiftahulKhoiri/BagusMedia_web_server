// ===== Ganti Foto Profil =====
const avatarInput = document.getElementById("avatarInput");
const avatarPreview = document.getElementById("avatarPreview");
const changeAvatarBtn = document.getElementById("changeAvatarBtn");

changeAvatarBtn.addEventListener("click", () => avatarInput.click());

avatarInput.addEventListener("change", () => {
    const file = avatarInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = e => {
            avatarPreview.src = e.target.result;
            localStorage.setItem("userAvatar", e.target.result);
        };
        reader.readAsDataURL(file);
    }
});

// ===== Simpan Nama & Email ke LocalStorage =====
const nameInput = document.getElementById("nameInput");
const emailInput = document.getElementById("emailInput");
const saveBtn = document.getElementById("saveBtn");

const profileName = document.getElementById("profileName");
const profileEmail = document.getElementById("profileEmail");

// Muat data tersimpan
window.addEventListener("load", () => {
    const savedName = localStorage.getItem("userName");
    const savedEmail = localStorage.getItem("userEmail");
    const savedAvatar = localStorage.getItem("userAvatar");

    if (savedName) profileName.textContent = savedName;
    if (savedEmail) profileEmail.textContent = savedEmail;
    if (savedAvatar) avatarPreview.src = savedAvatar;
});

// Simpan perubahan
saveBtn.addEventListener("click", () => {
    const newName = nameInput.value.trim();
    const newEmail = emailInput.value.trim();

    if (newName) {
        profileName.textContent = newName;
        localStorage.setItem("userName", newName);
    }

    if (newEmail) {
        profileEmail.textContent = newEmail;
        localStorage.setItem("userEmail", newEmail);
    }

    nameInput.value = "";
    emailInput.value = "";

    alert("Profil berhasil diperbarui!");
});