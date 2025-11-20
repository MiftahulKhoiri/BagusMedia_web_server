// ================================
// Realtime Monitor Bar
// ================================

async function updateMonitor() {
    try {
        const res = await fetch("/api/monitor");
        const d = await res.json();

        document.getElementById("cpu-val").innerText = d.cpu + "%";
        document.getElementById("cpu-bar").style.width = d.cpu + "%";

        document.getElementById("ram-val").innerText = d.ram_percent + "%";
        document.getElementById("ram-bar").style.width = d.ram_percent + "%";

        document.getElementById("disk-val").innerText = d.disk_percent + "%";
        document.getElementById("disk-bar").style.width = d.disk_percent + "%";
    } catch (e) {
        console.log("Monitor error:", e);
    }
}

setInterval(updateMonitor, 1000);
updateMonitor();


// ================================
// Realtime Charts
// ================================
let labels = [];
let cpuData = [], ramData = [], diskData = [];

function createChart(id, label, color) {
    return new Chart(document.getElementById(id), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label,
                data: [],
                borderColor: color,
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            animation: false,
            scales: { y: { min: 0, max: 100 } }
        }
    });
}

const cpuChart = createChart("cpuChart", "CPU %", "#0ff");
const ramChart = createChart("ramChart", "RAM %", "#9ff");
const diskChart = createChart("diskChart", "Disk %", "#cff");

async function updateCharts() {
    const res = await fetch("/api/monitor");
    const d = await res.json();

    const t = new Date().toLocaleTimeString();

    labels.push(t);
    if (labels.length > 20) labels.shift();

    cpuData.push(d.cpu); if (cpuData.length > 20) cpuData.shift();
    ramData.push(d.ram_percent); if (ramData.length > 20) ramData.shift();
    diskData.push(d.disk_percent); if (diskData.length > 20) diskData.shift();

    cpuChart.data.datasets[0].data = cpuData;
    ramChart.data.datasets[0].data = ramData;
    diskChart.data.datasets[0].data = diskData;

    cpuChart.update();
    ramChart.update();
    diskChart.update();
}

setInterval(updateCharts, 1000);