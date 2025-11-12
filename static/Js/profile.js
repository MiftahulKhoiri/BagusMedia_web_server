// ===== Partikel Neon Reaktif =====
const canvas = document.getElementById("neon-bg");
const ctx = canvas.getContext("2d");

let particles = [];
const colors = ["#00ffff", "#ff00ff", "#ffffff"];

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
            dx: (Math.random() - 0.5) * 0.6,
            dy: (Math.random() - 0.5) * 0.6,
            color: colors[Math.floor(Math.random() * colors.length)]
        });
    }
}
createParticles(100);

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

// ===== Simpan Profil =====
document.getElementById("save-profile").addEventListener("click", async () => {
    const data = {
        nama: document.getElementById("nama").value,
        email: document.getElementById("email").value,
        bio: document.getElementById("bio").value,
        foto: document.getElementById("profile-photo").src
    };

    const res = await fetch("/api/save-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await res.json();
    alert(result.message);
});

// ===== Ubah Foto Profil =====
const photoInput = document.getElementById("photo-input");
photoInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (ev) => {
            document.getElementById("profile-photo").src = ev.target.result;
        };
        reader.readAsDataURL(file);
    }
});