// =====================================================
// 🔒 SHOW / HIDE PASSWORD
// =====================================================
function togglePassword(id) {
    let pwd = document.getElementById(id);
    pwd.type = pwd.type === "password" ? "text" : "password";
}


// =====================================================
// 🔓 PROSES REGISTER KE SERVER
// =====================================================
function submitRegister() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirm = document.getElementById("confirm_password").value.trim();

    if (!username || !password || !confirm) {
        alert("Semua field harus diisi!");
        return;
    }

    if (password !== confirm) {
        alert("Password tidak sama!");
        return;
    }

    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(res => res.text())
    .then(result => {
        if (result.includes("Username sudah dipakai")) {
            alert("❗ Username sudah digunakan!");
        } else {
            window.location.href = "/login";
        }
    })
    .catch(err => {
        console.error("Register error:", err);
        alert("Terjadi kesalahan saat mencoba register!");
    });
}