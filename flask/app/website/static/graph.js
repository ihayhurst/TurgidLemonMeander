const slider = document.getElementById("hoursSlider");
const label = document.getElementById("hoursLabel");

async function loadGraph(hours) {
    const response = await fetch(`/graph-data?hours=${hours}`);
    const data = await response.json();

    const traces = [
        {
            x: data.time,
            y: data.temperature,
            name: "Temperature °C",
            yaxis: "y1",
            type: "scatter",
            mode: "lines",
            line: {
                color: "red",
                width: 2
            }
        },
        {
            x: data.time,
            y: data.humidity,
            name: "Humidity %",
            yaxis: "y2",
            type: "scatter",
            mode: "lines",
            line: {
                color: "green",
                width: 2,
            }
        },
        {
            x: data.time,
            y: data.pressure,
            name: "Pressure hPa",
            yaxis: "y3",
            type: "scatter",
            mode: "lines",
            line: {
                color: "blue",
                width: 2,
            }
        }
    ];
const isMobile = window.innerWidth < 768;
const layout = {
  title: "Temperature, Humidity and Pressure",
  margin: { r: 120 },

  yaxis: { title: "Temperature (°C)", range: [-10, 40], titlefont: { color: "red" }, tickfont: { color: "red" } },
  yaxis2: { title: "Humidity (%)", range: [0, 100], titlefont: { color: "green" }, tickfont: { color: "green" }, overlaying: "y", side: "right" },
  yaxis3: { title: "Pressure (hPa)", range: [940, 1053], titlefont: { color: "blue" }, tickfont: { color: "blue" }, overlaying: "y", side: "right", position: 1.1 },

  shapes: [
    // freezing point 0°C
    { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: 0, y1: 0, line: { color: "red", dash: "dash", width: 1 } },

    // mean sea-level pressure
    { type: "line", xref: "paper", x0: 0, x1: 1, yref: "y3", y0: 1013, y1: 1013, line: { color: "blue", dash: "dash", width: 1 } },

    // high/low pressure band
    { type: "rect", xref: "paper", x0: 0, x1: 1, yref: "y3", y0: 1010, y1: 1020, fillcolor: "rgba(173, 216, 230, 0.3)", line: { width: 0 } }
  ],
  height: isMobile ? 420 : 640,   // desktop taller
  legend: {
    orientation: "h",
    x: 0.5,
    xanchor: "center",
    y: -0.28,
    yanchor: "top",
    font: {
      size: isMobile ? 10 : 12
    }
  },
  margin: {
    t: 50,
    b: isMobile ? 110 : 130   // extra space for legend
  }
};


    Plotly.react("graph", traces, layout);
}

slider.addEventListener("input", () => {
    label.textContent = `${slider.value} hours`;
    loadGraph(slider.value);
});

loadGraph(slider.value);

