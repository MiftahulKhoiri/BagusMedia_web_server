// ===============================
// ⚙️ PROFIL JAVASCRIPT
// ===============================

const profilePhoto = document.getElementById('profile-photo');
const photoInput = document.getElementById('photo-input');
const editBtn = document.getElementById('edit-btn');

const nama = document.getElementById('nama');
const email = document.getElementById('email');
const bio = document.getElementById('bio');

let editMode = false;

// Klik foto → pilih gambar baru
profilePhoto.addEventListener('click', () => {
    if (editMode) photoInput.click();
});

// Preview foto otomatis
photoInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        profilePhoto.src = URL.createObjectURL(file);
    }
});

// Edit/Simpan Mode
editBtn.addEventListener('click', () => {
    editMode = !editMode;

    [nama, email, bio].forEach(input => input.readOnly = !editMode);
    editBtn.textContent = editMode ? 'Simpan Profil' : 'Edit Profil';

    if (!editMode) {
        // Simpan data ke server (contoh sederhana)
        const data = {
            nama: nama.value,
            email: email.value,
            bio: bio.value
        };
        console.log('Profil disimpan:', data);
        alert('Profil berhasil disimpan!');
    }
});