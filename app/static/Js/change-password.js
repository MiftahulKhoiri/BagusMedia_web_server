document.addEventListener("DOMContentLoaded", () => {

    const saveBtn = document.getElementById("save-pass");

    saveBtn.addEventListener("click", async () => {

        const oldPass = document.getElementById("old_password").value;
        const newPass = document.getElementById("new_password").value;
        const confirmPass = document.getElementById("confirm_password").value;

        if (newPass !== confirmPass) {
            alert("Password baru tidak sama!");
            return;
        }

        const res = await fetch("/api/change-password", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                old_password: oldPass,
                new_password: newPass
            })
        });

        const result = await res.json();

        if (result.status === "success") {
            alert("Password berhasil diubah!");
            window.location.href = "/profile";
        } else {
            alert(result.message);
        }

    });
});

document.addEventListener("DOMContentLoaded", () => {

    const saveBtn = document.getElementById("save-pass-btn");

    saveBtn.addEventListener("click", async () => {

        const oldPass = document.getElementById("old_password").value;
        const newPass = document.getElementById("new_password").value;
        const newPass2 = document.getElementById("new_password2").value;

        if (!oldPass || !newPass || !newPass2) {
            alert("Semua field harus diisi!");
            return;
        }

        if (newPass !== newPass2) {
            alert("Password baru tidak sama!");
            return;
        }

        const res = await fetch("/api/change-password", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                old_password: oldPass,
                new_password: newPass
            })
        });

        const result = await res.json();

        if (result.status === "success") {
            alert("Password berhasil diperbarui!");
            window.location.href = "/profile";
        } else {
            alert(result.message || "Gagal mengubah password!");
        }
    });
});