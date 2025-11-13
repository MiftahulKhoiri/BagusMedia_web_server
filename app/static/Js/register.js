// =====================================================
// 🌌 ANIMASI GALAKSI NEON
// =====================================================
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.onresize = resizeCanvas;

// Buat partikel neon
let particles = [];
for (let i = 0; i < 80; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 3 + 1,
        speedX: Math.random() * 1.4 - 0.7,  
        speedY: Math.random() * 1.4 - 0.7
    });
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        const neonColors = [
            { fill:"rgba(0,255,100,0.35)", glow:"#00ff80" },
            { fill:"rgba(0,200,255,0.35)", glow:"#00eaff" },
            { fill:"rgba(180,0,255,0.35)", glow:"#d400ff" }
        ];

        const c = neonColors[Math.floor(Math.random() * neonColors.length)];

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = c.fill;
        ctx.shadowColor = c.glow;
        ctx.shadowBlur = 20;
        ctx.fill();

        p.x += p.speedX;
        p.y += p.speedY;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;
    });

    requestAnimationFrame(animate);
}
animate();


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