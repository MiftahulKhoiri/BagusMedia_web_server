// ======================================================
// 🌌 Efek Partikel Neon Reaktif
// ======================================================
const canvas = document.getElementById("neon-particles");
const ctx = canvas.getContext("2d");

let particles = [];
const numParticles = 70;
let mouse = { x: null, y: null, radius: 120 };

// Atur ukuran awal canvas
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

// ======================================================
// 💡 Kelas Partikel
// ======================================================
class Particle {
    constructor(x, y, size, color, velocityX, velocityY) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
        this.velocityX = velocityX;
        this.velocityY = velocityY;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.shadowBlur = 15;
        ctx.shadowColor = this.color;
        ctx.fillStyle = this.color;
        ctx.fill();
    }

    update() {
        if (this.x + this.size > canvas.width || this.x - this.size < 0) {
            this.velocityX *= -1;
        }
        if (this.y + this.size > canvas.height || this.y - this.size < 0) {
            this.velocityY *= -1;
        }

        this.x += this.velocityX;
        this.y += this.velocityY;

        // Efek interaksi dengan mouse
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < mouse.radius + this.size) {
            this.x -= dx / 8;
            this.y -= dy / 8;
        }

        this.draw();
    }
}

// ======================================================
// 🔥 Inisialisasi Partikel
// ======================================================
function initParticles() {
    particles = [];
    for (let i = 0; i < numParticles; i++) {
        const size = Math.random() * 3 + 1;
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const velocityX = (Math.random() - 0.5) * 1.2;
        const velocityY = (Math.random() - 0.5) * 1.2;
        const neonColors = ["#00ffff", "#ff00ff", "#00ff80", "#ff0080"];
        const color = neonColors[Math.floor(Math.random() * neonColors.length)];
        particles.push(new Particle(x, y, size, color, velocityX, velocityY));
    }
}

// ======================================================
// 🌈 Animasi Partikel
// ======================================================
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let particle of particles) {
        particle.update();
    }

    // Garis penghubung antar partikel
    for (let i = 0; i < particles.length; i++) {
        for (let j = i; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100) {
                ctx.beginPath();
                ctx.strokeStyle = "rgba(0, 255, 255, 0.1)";
                ctx.lineWidth = 1;
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
                ctx.closePath();
            }
        }
    }

    requestAnimationFrame(animate);
}

// ======================================================
// 🖱️ Event Gerakan Mouse
// ======================================================
window.addEventListener("mousemove", (e) => {
    mouse.x = e.x;
    mouse.y = e.y;
});

window.addEventListener("mouseout", () => {
    mouse.x = undefined;
    mouse.y = undefined;
});

// ======================================================
// 🚀 Jalankan Efek
// ======================================================
initParticles();
animate();