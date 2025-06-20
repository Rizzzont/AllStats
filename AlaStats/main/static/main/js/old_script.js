const ctx = document.getElementById('myBarChart').getContext('2d');

const salesData = chartData.sales;
const revenueData = chartData.profit;

let currentData = revenueData;

const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: chartData.names,
        datasets: [{
            label: "Выручка",
            data: currentData,
            backgroundColor: "rgba(75, 192, 192, 0.6)",
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

function updateChart(type) {
    if (type === 'sales') {
        chart.data.datasets[0].data = salesData;
        chart.data.datasets[0].label = "Количество продаж";
        chart.data.datasets[0].backgroundColor = "rgba(13, 113, 107, 0.6)";
        chart.data.datasets[0].borderColor = "rgba(13, 113, 107, 1)";
    } else {
        chart.data.datasets[0].data = revenueData;
        chart.data.datasets[0].label = "Выручка";
        chart.data.datasets[0].backgroundColor = "rgba(75, 192, 192, 0.6)";
        chart.data.datasets[0].borderColor = "rgba(75, 192, 192, 1)";
    }
    chart.update();
}
function toggleMenu() {
    document.querySelector('.nav_right').classList.toggle('active');
}

// Открытие модального окна
function openModal() {
    document.getElementById("loginModal").style.display = "block";
}

// Закрытие модального окна
function closeModal() {
    document.getElementById("loginModal").style.display = "none";
}

// Закрытие окна при клике вне формы
window.onclick = function(event) {
    let modal = document.getElementById("loginModal");
    if (event.target === modal) {
        modal.style.display = "none";
    }
}

// Обработчик формы входа
document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Останавливаем перезагрузку страницы

    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;
    let errorMessage = document.getElementById("loginError");

    // Простая проверка (можно заменить на реальную авторизацию через сервер)
    if (email === "admin@example.com" && password === "123456") {
        alert("Успешный вход!");
        closeModal();
    } else {
        errorMessage.textContent = "Неверный email или пароль";
    }
});
