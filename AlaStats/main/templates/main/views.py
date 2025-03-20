from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from main.total_profit import TotalProfit
import pandas as pd


def index(request):
    totalprofit = 0

    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        filepath = fs.path(filename)

        df = pd.read_excel(filepath, usecols=["Выкупили на сумму, ₽"])
        tp = TotalProfit(df)
        totalprofit = tp.get_results()

    return render(request, "main/index.html", {"total_profit": totalprofit})
def analytics(request):
    return render(request, ("main/analytics.html"))


def recomendations(request):
    return render(request, ("main/recomendations.html"))


def private_requests(request):
    return render(request, ("main/private_requests.html"))