document.getElementById("daftarBtn").addEventListener("click", () => {
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();
    const confirm = document.getElementById("confirm_password").value.trim();

    if (!user || !pass || !confirm) {
        alert("Semua data harus diisi!");
        return;
    }

    if (pass !== confirm) {
        alert("Password tidak sama!");
        return;
    }

    // Kirim ke server
    fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password: pass })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            window.location.href = "/login";
        }
    });
});