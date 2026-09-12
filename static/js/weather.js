// weather.js
// Fetches the 5-day forecast + alerts, renders a simple bar/line chart
// (Chart.js via CDN) so farmers can see rainfall/temperature trends
// visually rather than reading numbers.

const getWeatherBtn = document.getElementById("get-weather-btn");
const resultBox = document.getElementById("result-box");
const spinner = document.getElementById("spinner");
let weatherChart = null;

const ALERT_ICONS = {
    rain_alert: "🌧️",
    heat_alert: "🔥",
    frost_alert: "❄️",
    normal_weather: "✅",
};

getWeatherBtn.addEventListener("click", async () => {
    const location = document.getElementById("location").value;
    if (!location) {
        alert("Please enter your location / உங்கள் இடத்தை உள்ளிடவும்");
        return;
    }

    spinner.style.display = "block";
    resultBox.classList.remove("show");

    try {
        const res = await fetch("/api/weather-alerts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ location }),
        });
        const data = await res.json();
        spinner.style.display = "none";

        if (data.error) {
            resultBox.innerHTML = `<p>${data.error}</p>`;
            resultBox.classList.add("show", "alert");
            return;
        }

        resultBox.classList.add("show");
        let html = `<p style="font-size:0.85rem;color:#666;">Source: ${data.forecast.source}</p>`;
        data.alerts.forEach((day, i) => {
            const flagsHtml = day.flags.map((f) => `<span>${ALERT_ICONS[f] || ""} ${f.replace("_", " ")}</span>`).join("");
            html += `
                <div class="weather-day-card">
                    <strong>${day.date}</strong>
                    <span>${data.forecast.days[i].temperature_c}&deg;C</span>
                    <span>${data.forecast.days[i].rainfall_mm}mm rain</span>
                    <span class="flags">${flagsHtml}</span>
                </div>
            `;
        });
        html += `<canvas id="weatherChart" height="180"></canvas>`;
        resultBox.innerHTML = html;

        renderChart(data.forecast.days);
    } catch (err) {
        spinner.style.display = "none";
        resultBox.innerHTML = `<p>Something went wrong. Please try again.</p>`;
        resultBox.classList.add("show", "alert");
        console.error(err);
    }
});

function renderChart(days) {
    const ctx = document.getElementById("weatherChart").getContext("2d");
    if (weatherChart) weatherChart.destroy();

    weatherChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: days.map((d) => d.date.slice(5)),
            datasets: [
                {
                    label: "Rainfall (mm)",
                    data: days.map((d) => d.rainfall_mm),
                    backgroundColor: "#3f7d3a",
                    yAxisID: "y",
                },
                {
                    label: "Temperature (°C)",
                    data: days.map((d) => d.temperature_c),
                    type: "line",
                    borderColor: "#e8b93f",
                    backgroundColor: "#e8b93f",
                    yAxisID: "y1",
                },
            ],
        },
        options: {
            responsive: true,
            scales: {
                y: { type: "linear", position: "left", title: { display: true, text: "Rainfall (mm)" } },
                y1: { type: "linear", position: "right", title: { display: true, text: "Temp (°C)" }, grid: { drawOnChartArea: false } },
            },
        },
    });
}
