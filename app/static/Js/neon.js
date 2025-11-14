// Membuat elemen canvas untuk efek neon
const canvas = document.createElement("canvas");
canvas.id = "neonCanvas";
document.body.appendChild(canvas);

const ctx = canvas.getContext("2d");

// Menyesuaikan ukuran canvas dengan ukuran layar
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.onresize = resize;

// Warna-warna neon yang digunakan
const colors = ["#ff00ff", "#00ffff", "#00ff00", "#ff8800", "#ff0000", "#00aaff"];

// Menyimpan daftar partikel (titik neon)
const particles = [];

// Membuat 60 partikel neon dengan posisi & arah acak
for (let i = 0; i < 60; i++) {
    particles.push({
        x: Math.random() * canvas.width,       // posisi X
        y: Math.random() * canvas.height,      // posisi Y
        size: Math.random() * 4 + 2,           // ukuran titik
        speedX: (Math.random() - 0.5) * 1.5,    // kecepatan arah X
        speedY: (Math.random() - 0.5) * 1.5,    // kecepatan arah Y
        color: colors[Math.floor(Math.random() * colors.length)], // warna
        alpha: Math.random(),                  // transparansi awal
        blinkSpeed: Math.random() * 0.03 + 0.01 // kecepatan kedip
    });
}

// Fungsi animasi utama
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // bersihkan layar

    particles.forEach(p => {
        // Gerakkan partikel
        p.x += p.speedX;
        p.y += p.speedY;

        // Pantulan jika menyentuh pinggir layar
        if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
        if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;

        // Efek kedip (neon berdenyut)
        p.alpha += p.blinkSpeed;
        if (p.alpha >= 1 || p.alpha <= 0) p.blinkSpeed *= -1;

        // Menggambar titik neon
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.shadowColor = p.color;
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
    });

    requestAnimationFrame(animate); // ulangi animasi
}

animate();