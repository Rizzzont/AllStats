document.addEventListener("DOMContentLoaded", function () {
    function createChart(chartId, type, labels, data, label) {
        const ctx = document.getElementById(chartId).getContext("2d");
        return new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)',
                        'rgba(153, 102, 255, 0.5)',
                        'rgba(255, 159, 64, 0.5)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: type === "bar" ? {
                    y: {
                        beginAtZero: true
                    }
                } : {}
            }
        });
    }

    function toggleChart(chartId) {
        let chart = charts[chartId];
        chart.config.type = chart.config.type === "bar" ? "line" : "bar";
        chart.update();
    }

    const labels = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"];
    const pieLabels = ["A", "B", "C", "D"];

    let charts = {
        "chartDiz": createChart("chartDiz", "bar", labels, [12, 19, 3, 5, 2, 3, 7, 10, 15, 20, 25, 30], "Продажи по артикулам дизайнеров"),
        "pieDiz": createChart("pieDiz", "pie", pieLabels, [10, 20, 30, 40], "Распределение"),
        "chartDizs": createChart("chartDizs", "bar", labels, [5, 9, 4, 7, 10, 12, 6, 8, 14, 18, 22, 27], "Прибыль по артикулам дизайнеров"),
        "pieDizs": createChart("pieDizs", "pie", pieLabels, [15, 25, 35, 25], "Распределение"),
        "chartCategory": createChart("chartCategory", "bar", labels, [8, 14, 6, 12, 18, 9, 13, 15, 22, 28, 30, 35], "Категория"),
        "pieCategory": createChart("pieCategory", "pie", pieLabels, [20, 15, 40, 25], "Распределение"),
    };

    window.toggleChart = toggleChart;
});
