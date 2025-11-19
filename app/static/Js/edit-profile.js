// profile.js - preview, upload photo, save profile

function showMsg(text, timeout=3000){
    const el = document.getElementById('msg');
    if(!el) return;
    el.style.display = 'block';
    el.textContent = text;
    setTimeout(()=> { el.style.display='none'; }, timeout);
}

function previewImage(input, previewId){
    if(!input.files || !input.files[0]) return;
    const file = input.files[0];
    const url = URL.createObjectURL(file);
    const img = document.getElementById(previewId);
    if(img) img.src = url;
}

// Upload photo to server via /api/upload-photo
async function uploadPhoto(inputElem, type){
    if(!inputElem.files || !inputElem.files[0]) return;
    const file = inputElem.files[0];
    const fd = new FormData();
    fd.append('photo', file);
    fd.append('type', type);

    showMsg('Uploading ' + type + ' ...');

    try{
        const res = await fetch('/api/upload-photo', { method:'POST', body: fd });
        const data = await res.json();

        if(data.status && data.status === 'success'){
            showMsg('Upload sukses!');
            // update preview already done by previewImage
            // optionally update server-side profile.json is already handled by backend
        } else {
            showMsg('Upload gagal: ' + (data.message || JSON.stringify(data)));
        }
    }catch(err){
        showMsg('Upload error: ' + err.message);
    }
}

// Save profile (name/email/jk/umur/bio) to /api/save-profile
async function saveProfile(){
    const nama = document.getElementById('nama').value || '';
    const email = document.getElementById('email').value || '';
    const jk = document.getElementById('jk').value || '';
    const umur = document.getElementById('umur').value || '';
    const bio = document.getElementById('bio').value || '';

    // basic validation
    if(nama.trim() === ''){
        showMsg('Nama tidak boleh kosong');
        return;
    }

    const payload = { nama, email, jk, umur, bio };

    showMsg('Menyimpan profil ...');

    try{
        const res = await fetch('/api/save-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.status === 'success'){
            showMsg('Profil tersimpan');
            // redirect to profile page after short delay
            setTimeout(()=> location.href = '{{ url_for("profile.profile_page") }}'.replace(/^{{\s*url_for\(|\)\s*}}$/g,''), 900);
        } else {
            showMsg('Simpan gagal');
        }
    }catch(err){
        showMsg('Error: ' + err.message);
    }
}