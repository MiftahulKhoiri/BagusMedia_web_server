// =======================================
// 🌌 ANIMASI GALAKSI NEON
// =======================================
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.onresize = resizeCanvas;

// PARTIKEL NEON
let particles = [];

for (let i = 0; i < 80; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 3 + 1,
        speedX: Math.random() * 1.4 - 0.7,  // lebih cepat
        speedY: Math.random() * 1.4 - 0.7
    });
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        const neonColors = [
            { fill:"rgba(0,255,100,0.35)", glow:"#00ff80" },  // hijau
            { fill:"rgba(0,200,255,0.35)", glow:"#00eaff" }, // biru
            { fill:"rgba(180,0,255,0.35)", glow:"#d400ff" }  // ungu
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

// =======================================
// 🔒 SHOW / HIDE PASSWORD
// =======================================
function togglePassword() {
    let pwd = document.getElementById("password");
    pwd.type = pwd.type === "password" ? "text" : "password";
}