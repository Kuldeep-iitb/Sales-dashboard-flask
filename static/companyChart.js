let companyTotalProcessed = Object.keys(companyTotalData).map((e) => ({
    name: e,
    value: companyTotalData[e],
    }));

let companyLabels = companyTotalProcessed.map((e) => e.name);
let companyValue = companyTotalProcessed.map((e) => e.value);

let companyTotal = document.getElementById("companyTotalYearChart").getContext("2d");

let companyTotalYearChart = new Chart(companyTotal, {
    type: "pie",
    data: {
        labels: companyLabels,
        datasets: [
            {
                label: "Deals per company",
                data: companyValue,
                backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 206, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(255, 159, 64, 0.2)",
                ],
                borderColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)",
                ],
                borderWidth: 1,
            },
        ],
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
            },
        },
    },
});