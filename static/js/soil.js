// soil.js
// Farmer types a location -> /api/soil-moisture returns 5-day weather,
// estimated soil moisture, Random Forest irrigation labels, and
// rule-based advice text. Renders a dashboard + a rainfall/humidity/
// moisture chart.

const analyzeBtn = document.getElementById("analyze-area-btn");
const resultBox = document.getElementById("result-box");
const spinner = document.getElementById("spinner");
let soilChart = null;

const BADGE_CLASS = { LOW: "low", MEDIUM: "medium", HIGH: "high" };

function dayLabel(index, dateStr, box) {
    if (index === 0) return box.dataset.dayToday;
    if (index === 1) return box.dataset.dayTomorrow;
    return `${box.dataset.dayN} ${index + 1}`;
}

analyzeBtn.addEventListener("click", async () => {
    const location = document.getElementById("location").value.trim();
    if (!location) {
        alert("Please enter your area / village / city \u2014 உங்கள் பகுதியை உள்ளிடவும்");
        return;
    }

    const payload = {
        location,
        soil_type: document.getElementById("soil_type").value,
        growth_stage: document.getElementById("growth_stage").value,
    };

    spinner.style.display = "block";
    resultBox.classList.remove("show", "alert");
    resultBox.innerHTML = "";

    try {
        const res = await fetch("/api/soil-moisture", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        spinner.style.display = "none";

        if (data.error) {
            resultBox.innerHTML = `<p>${data.error}</p>`;
            resultBox.classList.add("show", "alert");
            return;
        }

        renderDashboard(data);
    } catch (err) {
        spinner.style.display = "none";
        resultBox.innerHTML = `<p>Something went wrong. Please try again.</p>`;
        resultBox.classList.add("show", "alert");
        console.error(err);
    }
});

function renderDashboard(data) {
    const box = resultBox;
    const today = data.forecast[0];

    let html = `
        <h3>${data.location} \u2014 ${box.dataset.current}</h3>
        <div class="conditions-grid">
            <div class="condition-tile">🌡 <strong>${box.dataset.temp}</strong><span>${today.temperature_c}\u00b0C</span></div>
            <div class="condition-tile">💧 <strong>${box.dataset.humidity}</strong><span>${today.humidity_pct}%</span></div>
            <div class="condition-tile">🌧 <strong>${box.dataset.rainfall}</strong><span>${today.rainfall_mm}mm</span></div>
            <div class="condition-tile">🌱 <strong>${box.dataset.moisture}</strong><span>${today.estimated_soil_moisture_pct}%</span></div>
        </div>
        <p class="fine-print">${box.dataset.moistureNote}</p>

        <h4>${box.dataset.forecastHeading}</h4>
        <canvas id="soilChart" height="180"></canvas>

        <div class="forecast-cards">
    `;

    data.forecast.forEach((day, i) => {
        const badge = BADGE_CLASS[day.irrigation_label] || "medium";
        html += `
            <div class="forecast-card">
                <div class="forecast-day">${dayLabel(i, day.date, box)}</div>
                <span class="badge ${badge}">${day.irrigation_label}</span>
                <div class="forecast-meta">${day.rainfall_mm}mm · ${day.humidity_pct}% · ${day.estimated_soil_moisture_pct}% moist.</div>
            </div>
        `;
    });

    html += `</div><p class="fine-print">${data.model_note}</p>`;

    html += `
        <div class="advice-block">
            <h4>${box.dataset.irrigationHeading}</h4>
            <p>${data.irrigation_advice}</p>
        </div>
        <div class="advice-block">
            <h4>🌦️</h4>
            <p>${data.weather_situation}</p>
        </div>
        <div class="advice-block">
            <h4>${box.dataset.cropHeading}</h4>
            <p>${data.crop_maintenance}</p>
        </div>
        <div class="advice-block">
            <h4>${box.dataset.sowingHeading}</h4>
            <p>${data.sowing_guidance}</p>
            <p class="fine-print">${box.dataset.sowingDisclaimer}</p>
        </div>
    `;

    box.innerHTML = html;
    box.classList.add("show");

    renderChart(data.forecast);
}

function renderChart(days) {
    const ctx = document.getElementById("soilChart").getContext("2d");
    if (soilChart) soilChart.destroy();

    soilChart = new Chart(ctx, {
        data: {
            labels: days.map((d) => d.date.slice(5)),
            datasets: [
                {
                    type: "bar",
                    label: "Rainfall (mm)",
                    data: days.map((d) => d.rainfall_mm),
                    backgroundColor: "rgba(124,58,237,0.55)",
                    yAxisID: "y",
                },
                {
                    type: "line",
                    label: "Humidity (%)",
                    data: days.map((d) => d.humidity_pct),
                    borderColor: "#7ee787",
                    backgroundColor: "#7ee787",
                    yAxisID: "y1",
                    tension: 0.3,
                },
                {
                    type: "line",
                    label: "Estimated Soil Moisture (%)",
                    data: days.map((d) => d.estimated_soil_moisture_pct),
                    borderColor: "#d8b4fe",
                    backgroundColor: "#d8b4fe",
                    yAxisID: "y1",
                    tension: 0.3,
                    borderDash: [6, 4],
                },
            ],
        },
        options: {
            responsive: true,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { labels: { color: "#f5f3ff" } },
            },
            scales: {
                x: { ticks: { color: "#aaa5bd" }, grid: { color: "rgba(168,85,247,.08)" } },
                y: {
                    type: "linear", position: "left",
                    title: { display: true, text: "Rainfall (mm)", color: "#aaa5bd" },
                    ticks: { color: "#aaa5bd" }, grid: { color: "rgba(168,85,247,.08)" },
                },
                y1: {
                    type: "linear", position: "right", min: 0, max: 100,
                    title: { display: true, text: "% (humidity / moisture)", color: "#aaa5bd" },
                    ticks: { color: "#aaa5bd" }, grid: { drawOnChartArea: false },
                },
            },
        },
    });
}
