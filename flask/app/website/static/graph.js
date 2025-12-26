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
        },
        {
            x: data.time,
            y: data.humidity,
            name: "Humidity %",
            yaxis: "y2",
            type: "scatter",
        },
        {
            x: data.time,
            y: data.pressure,
            name: "Pressure hPa",
            yaxis: "y3",
            type: "scatter",
        }
    ];

    const layout = {
        xaxis: { title: "Time" },
        yaxis: { title: "Temperature °C" },
        yaxis2: {
            title: "Humidity %",
            overlaying: "y",
            side: "right"
        },
        yaxis3: {
            title: "Pressure hPa",
            overlaying: "y",
            side: "right",
            position: 0.95
        }
    };

    Plotly.react("graph", traces, layout);
}

slider.addEventListener("input", () => {
    label.textContent = `${slider.value} hours`;
    loadGraph(slider.value);
});

loadGraph(slider.value);

