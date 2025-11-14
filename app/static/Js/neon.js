// Buat canvas neon
const canvas = document.createElement("canvas");
canvas.id = "neonCanvas";
document.body.appendChild(canvas);

const ctx = canvas.getContext("2d");

// Resize canvas sesuai layar
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.onresize = resize;

// Warna neon random
const colors = ["#ff00ff", "#00ffff", "#00ff00", "#ff8800", "#ff0000", "#00aaff"];

// List partikel neon
const particles = [];

// Buat 60 partikel neon
for (let i = 0; i < 60; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: Math.random() * 4 + 2,
        speedX: (Math.random() - 0.5) * 1.5,
        speedY: (Math.random() - 0.5) * 1.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: Math.random(),
        blinkSpeed: Math.random() * 0.03 + 0.01
    });
}

// Animasi utama
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        p.x += p.speedX;
        p.y += p.speedY;

        // Pantulan pinggir layar
        if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
        if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;

        // Kedip neon
        p.alpha += p.blinkSpeed;
        if (p.alpha >= 1 || p.alpha <= 0) p.blinkSpeed *= -1;

        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.shadowColor = p.color;
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
    });

    requestAnimationFrame(animate);
}

animate();