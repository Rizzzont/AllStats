console.log("Обновление графика... выбран:", chartSelect.value, "введено:", itemInput.value);

document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('mainChart').getContext('2d');
    let chartType = 'bar';

    const chartSelect = document.getElementById('chartSelect');
    const extraInput = document.getElementById('extraInput');
    const itemInput = document.getElementById('itemInput');

    const currentChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: [],
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
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    async function fetchChartData(funcName, value = "") {
        const url = new URL("/api/analytics/", window.location.origin);
        url.searchParams.append("func", funcName);
        url.searchParams.append("value", value);

        console.log("Запрос к серверу:", url.toString());

        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Ошибка:", errorText);
                return { labels: [], values: [] };
            }
            return await response.json();
        } catch (error) {
            console.error("Ошибка сети:", error);
            return { labels: [], values: [] };
        }
    }

    async function updateChart() {
        const selectedChart = chartSelect.value;
        const userInput = itemInput.value.trim();

        const data = await fetchChartData(selectedChart, userInput);

        const labelText = chartSelect.options[chartSelect.selectedIndex].text;
        const inputSuffix = userInput ? ` (${userInput})` : "";

        currentChart.data.labels = data.labels || [];
        currentChart.data.datasets = [];

        currentChart.data.datasets.push({
            label: `Выкупили на сумму, ₽${inputSuffix}`,
            data: data.value_profit || [],
            backgroundColor: 'rgba(54, 162, 235, 0.5)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        });

        currentChart.data.datasets.push({
            label: `Заказали на сумму, ₽${inputSuffix}`,
            data: data.value_not_profit || [],
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        });

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

    itemInput.addEventListener('input', () => {
        const value = chartSelect.value;
        if (["chartDiz", "chartCategory", "chartGood"].includes(value)) {
            updateChart();
        }
    });

    document.getElementById('toggleChart').addEventListener('click', function () {
        currentChart.config.type = currentChart.config.type === 'bar' ? 'line' : 'bar';
        currentChart.update();
    });
});
