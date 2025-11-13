// ======================================================
// 🌌 Efek Partikel Neon untuk HOME
// ======================================================
const canvasHome = document.getElementById("neon-bg");
const ctxHome = canvasHome.getContext("2d");

let particlesHome = [];
const numParticlesHome = 80;
let mouseHome = { x: null, y: null, radius: 120 };

// Ukuran canvas otomatis
function resizeCanvasHome() {
    canvasHome.width = window.innerWidth;
    canvasHome.height = window.innerHeight;
}
resizeCanvasHome();
window.addEventListener("resize", resizeCanvasHome);

// ======================================================
// 🔹 Kelas Partikel
// ======================================================
class ParticleHome {
    constructor(x, y, size, color, velocityX, velocityY) {
        this.x = x;
        this.y = y;
        this.size = size;
        this.color = color;
        this.velocityX = velocityX;
        this.velocityY = velocityY;
    }

    draw() {
        ctxHome.beginPath();
        ctxHome.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctxHome.shadowBlur = 15;
        ctxHome.shadowColor = this.color;
        ctxHome.fillStyle = this.color;
        ctxHome.fill();
    }

    update() {
        if (this.x + this.size > canvasHome.width || this.x - this.size < 0) {
            this.velocityX *= -1;
        }
        if (this.y + this.size > canvasHome.height || this.y - this.size < 0) {
            this.velocityY *= -1;
        }

        this.x += this.velocityX;
        this.y += this.velocityY;

        // Efek mouse
        const dx = mouseHome.x - this.x;
        const dy = mouseHome.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < mouseHome.radius + this.size) {
            this.x -= dx / 8;
            this.y -= dy / 8;
        }

        this.draw();
    }
}

// ======================================================
// 🌈 Inisialisasi Partikel
// ======================================================
function initParticlesHome() {
    particlesHome = [];
    for (let i = 0; i < numParticlesHome; i++) {
        const size = Math.random() * 3 + 1;
        const x = Math.random() * canvasHome.width;
        const y = Math.random() * canvasHome.height;
        const velocityX = (Math.random() - 0.5) * 1.2;
        const velocityY = (Math.random() - 0.5) * 1.2;
        const colors = ["#00ccff", "#9933ff", "#3399ff", "#cc00ff"];
        const color = colors[Math.floor(Math.random() * colors.length)];
        particlesHome.push(new ParticleHome(x, y, size, color, velocityX, velocityY));
    }
}

// ======================================================
// 💫 Animasi Partikel
// ======================================================
function animateHome() {
    ctxHome.clearRect(0, 0, canvasHome.width, canvasHome.height);

    for (let p of particlesHome) {
        p.update();
    }

    // Garis konektor halus
    for (let i = 0; i < particlesHome.length; i++) {
        for (let j = i; j < particlesHome.length; j++) {
            const dx = particlesHome[i].x - particlesHome[j].x;
            const dy = particlesHome[i].y - particlesHome[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100) {
                ctxHome.beginPath();
                ctxHome.strokeStyle = "rgba(0, 200, 255, 0.15)";
                ctxHome.lineWidth = 1;
                ctxHome.moveTo(particlesHome[i].x, particlesHome[i].y);
                ctxHome.lineTo(particlesHome[j].x, particlesHome[j].y);
                ctxHome.stroke();
                ctxHome.closePath();
            }
        }
    }

    requestAnimationFrame(animateHome);
}

// ======================================================
// 🖱️ Mouse Listener
// ======================================================
window.addEventListener("mousemove", (e) => {
    mouseHome.x = e.x;
    mouseHome.y = e.y;
});

window.addEventListener("mouseout", () => {
    mouseHome.x = undefined;
    mouseHome.y = undefined;
});

// ======================================================
// 🚀 Jalankan
// ======================================================
initParticlesHome();
animateHome();