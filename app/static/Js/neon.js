// Membuat canvas full-screen untuk efek aurora neon
const canvas = document.createElement("canvas");
canvas.id = "neonCanvas";
document.body.appendChild(canvas);

const ctx = canvas.getContext("2d");

// Resize canvas sesuai ukuran layar
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener("resize", resize);

// Warna aurora neon (akan terus berubah)
let auroraColors = [
    "#ff00ff", "#ff33cc", "#ff0099",
    "#00ffff", "#33ccff", "#0099ff",
    "#39FF14", "#55ff33", "#00ff99",
    "#ff8800", "#ff4444", "#ff0066"
];

// Fungsi menghasilkan warna neon random
function randomColor() {
    return auroraColors[Math.floor(Math.random() * auroraColors.length)];
}

// Objek gelombang aurora
class AuroraWave {
    constructor() {
        this.y = Math.random() * canvas.height;
        this.speed = Math.random() * 0.4 + 0.2;
        this.color = randomColor();
        this.alpha = Math.random() * 0.35 + 0.25;
        this.amplitude = Math.random() * 120 + 50; // tinggi gelombang
        this.wavelength = Math.random() * 0.005 + 0.001; // panjang gelombang
        this.offset = Math.random() * 1000;
        this.colorDelay = Math.random() * 200 + 80;
    }

    update(t) {
        // Warna berubah otomatis
        this.colorDelay--;
        if (this.colorDelay <= 0) {
            this.color = randomColor();
            this.colorDelay = Math.random() * 200 + 80;
        }

        // Gerak gelombang perlahan turun
        this.y += this.speed;
        if (this.y > canvas.height + 100) {
            this.y = -100;
        }

        // Gambar gelombang neon
        ctx.beginPath();
        ctx.moveTo(0, this.y);

        for (let x = 0; x <= canvas.width; x++) {
            let waveY = this.y + Math.sin(x * this.wavelength + this.offset + t * 0.002) * this.amplitude;
            ctx.lineTo(x, waveY);
        }

        ctx.strokeStyle = this.color;
        ctx.globalAlpha = this.alpha;
        ctx.lineWidth = 3 + Math.sin(t * 0.002) * 1.2;
        ctx.shadowBlur = 30;
        ctx.shadowColor = this.color;
        ctx.stroke();

        // Offset untuk animasi gelombang bergerak
        this.offset += 0.01;
    }
}

// Membuat beberapa gelombang aurora neon
let waves = [];
for (let i = 0; i < 6; i++) {
    waves.push(new AuroraWave());
}

// Animasi utama
function animate(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    waves.forEach(wave => {
        wave.update(t);
    });

    requestAnimationFrame(animate);
}

animate(0);