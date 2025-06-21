document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('mainChart').getContext('2d');
    let chartType = 'bar';

    const labels = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"];
    
    const dataSets = {
        default: [],
        chartDiz: [12, 19, 3, 5, 2, 3, 7, 10, 15, 20, 25, 30],
        chartDizs: [5, 9, 4, 7, 10, 12, 6, 8, 14, 18, 22, 27],
        chartCategory: [8, 14, 6, 12, 18, 9, 13, 15, 22, 28, 30, 35],
        chartCategorys: [7, 11, 5, 10, 16, 8, 12, 14, 20, 25, 29, 33],
        chartGood: [9, 13, 7, 11, 17, 10, 14, 16, 21, 26, 31, 34],
        chartGoods: [4, 8, 2, 6, 9, 5, 7, 11, 13, 15, 19, 23]
    };

    const chartSelect = document.getElementById('chartSelect');
    const extraInput = document.getElementById('extraInput');
    const itemInput = document.getElementById('itemInput');

    let currentChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Выберите график',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });

    function updateChart() {
        const selectedChart = chartSelect.value;
        const userInput = itemInput.value;

        let labelText = chartSelect.options[chartSelect.selectedIndex].text;
        if (userInput.trim()) {
            labelText += ` (${userInput.trim()})`;
        }

        currentChart.data.datasets[0].label = labelText;
        currentChart.data.datasets[0].data = dataSets[selectedChart] || [];
        currentChart.update();
    }

    chartSelect.addEventListener('change', function () {
        const value = this.value;

        if (["chartDiz", "chartCategory", "chartGood"].includes(value)) {
            extraInput.classList.remove('hidden');
        } else {
            extraInput.classList.add('hidden');
            itemInput.value = "";
        }

        updateChart();
    });

    itemInput.addEventListener('input', updateChart);

    document.getElementById('toggleChart').addEventListener('click', function () {
        currentChart.config.type = currentChart.config.type === 'bar' ? 'line' : 'bar';
        currentChart.update();
    });
});
