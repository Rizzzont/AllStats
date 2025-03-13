from django.shortcuts import render
import pandas as pd
from django.core.files.storage import FileSystemStorage


class TotalProfit:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_results(self):
        total = 0
        for index, row in self.dataframe.iterrows():
            total += int(row["Заказали на сумму, ₽"])
        return total


def index(request):
    total_profit = None  # По умолчанию

    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)  # Сохраняем файл
        filepath = fs.path(filename)  # Получаем путь к файлу

        # Читаем Excel
        df = pd.read_excel(filepath, sheet_name="Товары")

        # Считаем сумму
        tp = TotalProfit(df)
        total_profit = tp.get_results()

    return render(request, ("main/index.html"), {"total_profit": total_profit})


def analytics(request):
    return render(request, ("main/analytics.html"))


def recomendations(request):
    return render(request, ("main/recomendations.html"))


def private_requests(request):
    return render(request, ("main/private_requests.html"))
