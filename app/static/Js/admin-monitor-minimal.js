// static/Js/admin-monitor-minimal.js
(function() {
  const term = document.getElementById("term-output");
  const cpuFill = document.getElementById("cpu-fill");
  const ramFill = document.getElementById("ram-fill");
  const diskFill = document.getElementById("disk-fill");
  const cpuText = document.getElementById("cpu-text");
  const ramText = document.getElementById("ram-text");
  const diskText = document.getElementById("disk-text");
  const uptimeText = document.getElementById("uptime-text");
  const clearBtn = document.getElementById("term-clear");
  const autoScrollCheckbox = document.getElementById("autoscroll");

  // Safety: jika element tidak ada (file dipakai di tempat lain)
  if(!term) return;

  function appendLog(line) {
    const time = new Date().toLocaleTimeString();
    term.textContent += `[${time}] ${line}\n`;
    if(autoScrollCheckbox.checked) {
      term.scrollTop = term.scrollHeight;
    }
  }

  function setBar(el, percent) {
    percent = Math.max(0, Math.min(100, Number(percent) || 0));
    el.style.width = percent + "%";
  }

  clearBtn.addEventListener("click", () => term.textContent = "");

  // fetch monitor API
  async function fetchMonitor() {
    try {
      const res = await fetch("/api/monitor", {cache: "no-cache"});
      if(!res.ok) throw new Error("HTTP " + res.status);
      const d = await res.json();

      // normalize values
      const cpu = Number(d.cpu) || 0;
      const ram = Number(d.ram_percent || d.ram_percent === 0 ? d.ram_percent : Math.round((d.ram_used/d.ram_total)*100)) || 0;
      const disk = Number(d.disk_percent || 0) || 0;
      const uptime = d.uptime || d.uptime || "N/A";

      // update UI
      cpuText.textContent = `${cpu}%`;
      ramText.textContent = `${ram}%`;
      diskText.textContent = `${disk}%`;
      uptimeText.textContent = uptime;

      setBar(cpuFill, cpu);
      setBar(ramFill, ram);
      setBar(diskFill, disk);

      // smart logging: only log when changes significant
      appendLog(`CPU ${cpu}% | RAM ${ram}% | DISK ${disk}% | UP ${uptime}`);

      // visual alarm on very high CPU
      if(cpu >= 90) {
        cpuFill.style.background = "linear-gradient(90deg,#ff7070,#ff1f1f)";
      } else {
        cpuFill.style.background = "linear-gradient(90deg,#70ff70,#1fab1f)";
      }

    } catch (e) {
      appendLog("ERROR fetching monitor: " + e.message);
    }
  }

  // initial
  fetchMonitor();

  // poll every 1s (light)
  const INTERVAL = 1000;
  setInterval(fetchMonitor, INTERVAL);
})();