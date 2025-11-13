// =====================================================
// ✨ PROFIL LOGIC — DIBUAT MUDAH DIPAHAMI
// =====================================================

// Ambil elemen dari HTML
const profilePhoto = document.getElementById('profile-photo');
const photoInput = document.getElementById('photo-input');

const editBtn = document.getElementById('edit-btn');
const nama = document.getElementById('nama');
const email = document.getElementById('email');
const bio = document.getElementById('bio');

// Mode edit (false = tidak edit, true = sedang edit)
let editMode = false;

// -----------------------------------------------------
// 👉 Klik foto profil = buka menu pilih gambar (jika mode edit)
// -----------------------------------------------------
profilePhoto.addEventListener('click', () => {
    if (editMode) photoInput.click();
});

// -----------------------------------------------------
// 👉 Preview foto otomatis
// -----------------------------------------------------
photoInput.addEventListener('change', (event) => {
    const file = event.target.files[0];

    // Jika user memilih file, tampilkan preview
    if (file) {
        profilePhoto.src = URL.createObjectURL(file);
    }
});

// -----------------------------------------------------
// 👉 Tombol EDIT ↔ SIMPAN
// -----------------------------------------------------
editBtn.addEventListener('click', () => {

    // Toggle mode edit
    editMode = !editMode;

    // Aktifkan / nonaktifkan input
    [nama, email, bio].forEach(el => el.readOnly = !editMode);

    // Ubah teks tombol
    editBtn.textContent = editMode ? 'Simpan Profil' : 'Edit Profil';

    // Jika user mengklik "Simpan Profil"
    if (!editMode) {

        // Ambil data terbaru
        const data = {
            nama: nama.value,
            email: email.value,
            bio: bio.value
        };

        // Kirim ke server dengan fetch
        fetch("/api/save-profile", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(response => {
            alert("Profil berhasil disimpan!");
        })
        .catch(err => {
            alert("Gagal menyimpan profil!");
        });
    }
});