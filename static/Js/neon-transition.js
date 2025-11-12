// =========================================================
// ⚡ NEON PARTICLE REACTIVE BACKGROUND
// =========================================================

const canvas = document.getElementById('neon-particles');
const ctx = canvas.getContext('2d');

let particlesArray = [];
const colors = ['#0ff', '#f0f', '#0ff', '#ff00ff', '#00ffff'];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Membuat partikel
class Particle {
    constructor(x, y, directionX, directionY, size, color) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.color = color;
        this.glow = Math.random() * 10 + 5;
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.shadowBlur = this.glow;
        ctx.shadowColor = this.color;
        ctx.fillStyle = this.color;
        ctx.fill();
    }
    update() {
        if (this.x + this.size > canvas.width || this.x - this.size < 0)
            this.directionX = -this.directionX;
        if (this.y + this.size > canvas.height || this.y - this.size < 0)
            this.directionY = -this.directionY;

        this.x += this.directionX;
        this.y += this.directionY;

        this.draw();
    }
}

// Inisialisasi partikel
function initParticles() {
    particlesArray = [];
    let count = (canvas.width * canvas.height) / 9000;
    for (let i = 0; i < count; i++) {
        let size = Math.random() * 2 + 1;
        let x = Math.random() * (canvas.width - size * 2) + size;
        let y = Math.random() * (canvas.height - size * 2) + size;
        let directionX = (Math.random() * 0.6) - 0.3;
        let directionY = (Math.random() * 0.6) - 0.3;
        let color = colors[Math.floor(Math.random() * colors.length)];
        particlesArray.push(new Particle(x, y, directionX, directionY, size, color));
    }
}

// Efek garis antar partikel
function connectParticles() {
    let opacityValue = 0.05;
    for (let a = 0; a < particlesArray.length; a++) {
        for (let b = a; b < particlesArray.length; b++) {
            let dx = particlesArray[a].x - particlesArray[b].x;
            let dy = particlesArray[a].y - particlesArray[b].y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 100) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 255, 255, ${opacityValue})`;
                ctx.lineWidth = 0.3;
                ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                ctx.stroke();
                ctx.closePath();
            }
        }
    }
}

// Animasi
function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
    }
    connectParticles();
}

initParticles();
animate();

// Efek respon klik
canvas.addEventListener('click', (e) => {
    for (let i = 0; i < 5; i++) {
        particlesArray.push(
            new Particle(e.x, e.y,
                (Math.random() - 0.5) * 2,
                (Math.random() - 0.5) * 2,
                Math.random() * 3 + 1,
                colors[Math.floor(Math.random() * colors.length)]
            )
        );
    }
});