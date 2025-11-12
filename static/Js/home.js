// ===== Partikel Neon Reaktif =====
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

let particles = [];
const colors = ["#ffcc00", "#00ffff", "#ff00ff", "#ffffff"];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resizeCanvas);
resizeCanvas();

function createParticles(count) {
    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            r: Math.random() * 2 + 1,
            dx: (Math.random() - 0.5) * 0.8,
            dy: (Math.random() - 0.5) * 0.8,
            color: colors[Math.floor(Math.random() * colors.length)]
        });
    }
}
createParticles(120);

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.shadowBlur = 8;
        ctx.shadowColor = p.color;
        ctx.fill();

        p.x += p.dx;
        p.y += p.dy;

        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
    }
    requestAnimationFrame(drawParticles);
}
drawParticles();

// ===== Efek hover kecil pada dropdown =====
const dropbtn = document.querySelector(".dropbtn");
dropbtn.addEventListener("mouseover", () => {
    dropbtn.style.textShadow = "0 0 8px #ffcc00";
});
dropbtn.addEventListener("mouseout", () => {
    dropbtn.style.textShadow = "none";
});