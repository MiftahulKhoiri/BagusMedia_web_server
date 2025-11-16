document.addEventListener("DOMContentLoaded", () => {

    const oldPass = document.getElementById("old_password");
    const newPass = document.getElementById("new_password");
    const confirmPass = document.getElementById("confirm_password");
    const saveBtn = document.getElementById("save-password");

    saveBtn.addEventListener("click", async () => {

        if (newPass.value !== confirmPass.value) {
            alert("Password baru dan konfirmasi tidak sama!");
            return;
        }

        const bodyData = {
            old_password: oldPass.value,
            new_password: newPass.value
        };

        const res = await fetch("/api/change-password", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(bodyData)
        });

        const result = await res.json();

        if (result.status === "success") {
            alert("Password berhasil diubah!");
            window.location.href = "/profile";
        } else {
            alert(result.message || "Gagal mengubah password!");
        }

    });

});