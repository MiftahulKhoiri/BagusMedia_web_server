// ================================
// 💫 Efek Transisi Neon Antar Halaman
// ================================

document.addEventListener('DOMContentLoaded', () => {
    // Tambahkan elemen neon transition ke body
    const neon = document.createElement('div');
    neon.id = 'neon-transition';
    document.body.appendChild(neon);

    // Tambahkan efek ke semua tautan internal
    document.querySelectorAll('a[href]').forEach(link => {
        const url = link.getAttribute('href');
        if (!url || url.startsWith('http') || url.startsWith('#')) return;

        link.addEventListener('click', (e) => {
            e.preventDefault();
            neon.classList.add('active');

            // Tunggu animasi selesai baru ganti halaman
            setTimeout(() => {
                window.location.href = url;
            }, 500);
        });
    });
});