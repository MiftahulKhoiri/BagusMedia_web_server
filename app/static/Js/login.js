// ==============================
// 🌟 ANIMASI NEON BERGERAK
// ==============================

// Ambil canvas
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

// Sesuaikan ukuran canvas
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.onresize = resizeCanvas;

// Animasi titik neon
let particles = [];

for (let i = 0; i < 40; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 3 + 1,
        speedX: Math.random() * 0.6 - 0.3,
        speedY: Math.random() * 0.6 - 0.3
    });
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0,255,100,0.25)";
        ctx.shadowColor = "#00ff80";
        ctx.shadowBlur = 15;
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


// ==============================
// 🔒 SHOW / HIDE PASSWORD
// ==============================

function togglePassword() {
    const pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
}