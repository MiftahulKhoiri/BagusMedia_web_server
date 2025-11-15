// ============================================
//  Efek Neon untuk Tombol & Foto Profil
//  ===========================================

// Tombol edit & logout glowing saat disentuh
const editBtn = document.querySelector(".btn-edit");
const logoutBtn = document.querySelector(".btn-logout");

function addNeonHover(button, color) {
    button.addEventListener("mouseenter", () => {
        button.style.boxShadow = `0 0 15px ${color}`;
        button.style.transform = "scale(1.05)";
    });

    button.addEventListener("mouseleave", () => {
        button.style.boxShadow = "none";
        button.style.transform = "scale(1.0)";
    });
}

// warna cyan untuk Edit
if (editBtn) addNeonHover(editBtn, "cyan");
// warna merah neon untuk Logout
if (logoutBtn) addNeonHover(logoutBtn, "red");


// ============================================
//  Efek Animasi Foto Profil
// ============================================

const photo = document.getElementById("profile-photo");

if (photo) {
    photo.style.transition = "0.3s";

    photo.addEventListener("mouseenter", () => {
        photo.style.transform = "scale(1.03)";
        photo.style.boxShadow = "0 0 20px cyan";
    });

    photo.addEventListener("mouseleave", () => {
        photo.style.transform = "scale(1.0)";
        photo.style.boxShadow = "none";
    });
}


// ============================================
//  Efek Glow pada Kolom Informasi
// ============================================

const infoBox = document.querySelector(".info-box");

if (infoBox) {
    infoBox.addEventListener("mouseenter", () => {
        infoBox.style.boxShadow = "0 0 15px rgba(0,255,255,0.4)";
        infoBox.style.borderColor = "cyan";
    });

    infoBox.addEventListener("mouseleave", () => {
        infoBox.style.boxShadow = "none";
        infoBox.style.borderColor = "rgba(0,255,255,0.25)";
    });
}


// ============================================
//  Efek animasi nama pengguna
// ============================================

const nameTag = document.querySelector(".profile-name h2");

if (nameTag) {
    nameTag.style.transition = "0.4s";

    nameTag.addEventListener("mouseenter", () => {
        nameTag.style.letterSpacing = "2px";
        nameTag.style.textShadow = "0 0 12px cyan";
    });

    nameTag.addEventListener("mouseleave", () => {
        nameTag.style.letterSpacing = "0px";
        nameTag.style.textShadow = "0 0 6px cyan";
    });
}


// ============================================
//  Console Log (debug ringan)
// ============================================
console.log("Profile.js loaded — Neon UI Active");