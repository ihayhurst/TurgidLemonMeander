let currentEnd = new Date(); // default = now
let windowHours = 48;

document.addEventListener("DOMContentLoaded", () => {

    const slider = document.getElementById("hoursSlider");
    const label  = document.getElementById("hoursLabel");
    const prevBtn = document.getElementById("prevDay");
    const nextBtn = document.getElementById("nextDay");

    // Initialise state FROM slider
    windowHours = parseInt(slider.value);
    label.textContent = `${windowHours} hours`;

    // Initial draw
    drawGraph();

    // Slider changes window width
    slider.addEventListener("input", () => {
        windowHours = parseInt(slider.value);
        label.textContent = `${windowHours} hours`;
        drawGraph();
    });

    // Shift back one day
    prevBtn.onclick = () => {
        console.log("Prev day clicked");
        currentEnd = new Date(currentEnd.getTime() - 24 * 3600 * 1000);
        drawGraph();
    };

    // Shift forward one day
    nextBtn.onclick = () => {
        console.log("Next day clicked");
        currentEnd = new Date(currentEnd.getTime() + 24 * 3600 * 1000);
        drawGraph();
    };
    
});

async function drawGraph() {
    console.log(
  "drawGraph window:",
  windowHours,
  "hours",
  "end:",
  currentEnd.toISOString()
);


    const start = new Date(
        currentEnd.getTime() - windowHours * 3600 * 1000
    );

    const startISO = start.toISOString();
    const endISO   = currentEnd.toISOString();
    // alternative call slider for last 168 hours
    //const response = await fetch(
    //    `/graph-data?hours=${windowHours}`
    //);
    const response = await fetch(
        `/graph-data?start=${startISO}&end=${endISO}`
    );
    if (!response.ok) {
      const text = await response.text();
      return;
    }

    const data = await response.json();

// ---- Pressure trend UI ----
const trendEl = document.getElementById("pressure-trend");
const trend = data.pressure_trend;

if (!trend) {
    trendEl.textContent = "";
    trendEl.className = "trend";
    return;
}

const arrow =
    trend.direction === "up"   ? "↑" :
    trend.direction === "down" ? "↓" :
                                 "→";

const sign = trend.delta_hpa > 0 ? "+" : "";

trendEl.textContent =
    `${arrow} ${sign}${trend.delta_hpa} hPa (last ${trend.hours}h)`;

trendEl.className = "trend";
if (trend.warning) {
    trendEl.classList.add("warning");
}


    const traces = [
        {
            x: data.time,
            y: data.temperature,
            name: "Temperature °C",
            yaxis: "y",
            type: "scatter",
            mode: "lines",
            line: { color: "red", width: 2 }
        },
        {
            x: data.time,
            y: data.humidity,
            name: "Humidity %",
            yaxis: "y2",
            type: "scatter",
            mode: "lines",
            line: { color: "green", width: 2, shape: "spline", smoothing: 1.3, simplify: true },
            connectgaps: false
        },
        {
            x: data.time,
            y: data.pressure,
            name: "Pressure hPa",
            yaxis: "y3",
            type: "scatter",
            mode: "lines",
            line: { color: "blue", width: 2 }
        },
        {
            x: data.time,
            y: data.dewpoint,
            name: "Dew Point °C",
            yaxis: "y",
            type: "scatter",
            mode: "lines",
            line: { color: "purple", width: 1, dash: "dot" }
}


    ];


    const isMobile = window.innerWidth < 768;
    const fogShapes = [];

    for (let i = 0; i < data.time.length; i++) {
    if (data.dewpoint_spread[i] <= 2) {
    fogShapes.push({
      type: "rect",
      xref: "x",
      yref: "paper",
      x0: data.time[i],
      x1: data.time[i + 1] || data.time[i],
      y0: 0,
      y1: 1,
      fillcolor: "rgba(180,180,255,0.15)",
      line: { width: 0 }
    });
  }
}

    const layout = {
        title: "Temperature, Humidity and Pressure",

        yaxis: {
            title: "Temperature (°C)",
            range: [-10, 40]
        },
        yaxis2: {
            title: "Humidity (%)",
            range: [0, 100],
            overlaying: "y",
            side: "right"
        },
        yaxis3: {
            title: "Pressure (hPa)",
            range: [940, 1053],
            overlaying: "y",
            side: "right",
            position: 1.08
        },
        
        shapes: [
    // freezing point 0°C
    { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: 0, y1: 0, line: { color: "red", dash: "dash", width: 1 } },

    // mean sea-level pressure
    { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y3", y0: 1013, y1: 1013, line: { color: "blue", dash: "dash", width: 1 } },

    // high/low pressure band
    { type: "rect", xref: "paper", x0: 0, x1: 1, yref: "y3", y0: 1010, y1: 1020, fillcolor: "rgba(173, 216, 230, 0.3)", line: { width: 0 } },
    ...fogShapes
  ],

        height: isMobile ? 420 : 640,
        margin: { t: 50, b: isMobile ? 110 : 130, r: 120 }
    };

    Plotly.react("graph", traces, layout, { responsive: true });
}

