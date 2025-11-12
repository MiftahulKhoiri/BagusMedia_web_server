// ==========================
// 🌌 Partikel Neon Reaktif
// ==========================
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

let particles = [];
const colors = ["#ffcc00", "#00ffff", "#ff00ff", "#ffffff"];
let globalAlpha = 0;

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
    ctx.globalAlpha = globalAlpha;

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

window.addEventListener("load", () => {
    let opacity = 0;
    const fadeIn = setInterval(() => {
        opacity += 0.02;
        globalAlpha = opacity;
        if (opacity >= 1) clearInterval(fadeIn);
    }, 40);
});

// ==========================
// 📱 Tombol Menu Mobile
// ==========================
const menuToggle = document.getElementById("menu-toggle");
const menu = document.querySelector(".menu");

if (menuToggle) {
    menuToggle.addEventListener("click", () => {
        menu.classList.toggle("show");
        menuToggle.textContent = menu.classList.contains("show") ? "✕" : "☰";
    });
}

// ==========================
// 🔽 Dropdown Menu Klik (Desktop + Mobile)
// ==========================
const dropbtn = document.querySelector(".dropbtn");
const dropdownContent = document.querySelector(".dropdown-content");

// Pastikan dropdown bisa diklik, bukan cuma hover
if (dropbtn && dropdownContent) {
    dropbtn.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownContent.classList.toggle("show-dropdown");
    });

    // Tutup dropdown jika klik di luar area
    window.addEventListener("click", (e) => {
        if (!dropdownContent.contains(e.target) && e.target !== dropbtn) {
            dropdownContent.classList.remove("show-dropdown");
        }
    });
}

// Tambahkan efek hover neon
if (dropbtn) {
    dropbtn.addEventListener("mouseover", () => {
        dropbtn.style.textShadow = "0 0 8px #ffcc00";
    });
    dropbtn.addEventListener("mouseout", () => {
        dropbtn.style.textShadow = "none";
    });
}