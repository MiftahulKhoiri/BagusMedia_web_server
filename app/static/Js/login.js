// =====================================================
// 🔒 SHOW / HIDE PASSWORD
// =====================================================
function togglePassword() {
    let pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
}


// =====================================================
// 🔐 PROSES LOGIN KE SERVER
// =====================================================
function submitLogin() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (username === "" || password === "") {
        alert("Username dan password harus diisi!");
        return;
    }

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(res => res.text())
    .then(result => {
        // Jika login gagal
        if (result.includes("Username atau password salah")) {
            alert("❗ Username atau Password salah!");
        } 
        else {
            // Jika login sukses → masuk ke HOME
            window.location.href = "/home";
        }
    })
    .catch(err => {
        console.error("Login error:", err);
        alert("Terjadi kesalahan saat mencoba login!");
    });
}