(async function () {
  const res = await fetch("predictions/latest.json");
  const data = await res.json();

  // Updated timestamp
  const updatedEl = document.getElementById("updated");
  updatedEl.textContent = "Last updated: " + new Date(data.generated_at).toLocaleString();

  const actuals = data.actuals;
  const preds = data.predictions;

  // Stats from predictions
  const predVals = preds.map((d) => d.demand_mw);
  const peak = Math.max(...predVals);
  const min = Math.min(...predVals);
  const avg = predVals.reduce((a, b) => a + b, 0) / predVals.length;
  const peakHour = new Date(preds[predVals.indexOf(peak)].datetime).getHours();

  const statsEl = document.getElementById("stats");
  const stats = [
    { label: "Peak", value: Math.round(peak).toLocaleString() + " MW" },
    { label: "Min", value: Math.round(min).toLocaleString() + " MW" },
    { label: "Avg", value: Math.round(avg).toLocaleString() + " MW" },
    { label: "Peak Hour", value: peakHour + ":00" },
  ];
  statsEl.innerHTML = stats
    .map(
      (s) =>
        `<div class="stat"><div class="stat-label">${s.label}</div><div class="stat-value">${s.value}</div></div>`
    )
    .join("");

  // Chart
  const fmt = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" }) +
      " " + d.getHours() + ":00";
  };

  const labels = [...actuals, ...preds].map((d) => fmt(d.datetime));
  const actualData = actuals.map((d) => d.demand_mw);
  const predData = new Array(actuals.length).fill(null).concat(predVals);

  // Bridge: connect last actual to first prediction
  predData[actuals.length - 1] = actualData[actualData.length - 1];

  new Chart(document.getElementById("chart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Actual (24h)",
          data: actualData,
          borderColor: "#4fc3f7",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
        {
          label: "Forecast (48h)",
          data: predData,
          borderColor: "#ff8a65",
          borderDash: [6, 3],
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          ticks: { color: "#888", maxRotation: 45, maxTicksLimit: 12 },
          grid: { color: "#222" },
        },
        y: {
          ticks: { color: "#888", callback: (v) => (v / 1000).toFixed(0) + "k" },
          grid: { color: "#222" },
          title: { display: true, text: "MW", color: "#888" },
        },
      },
      plugins: {
        legend: { labels: { color: "#ccc" } },
      },
    },
  });
})();
