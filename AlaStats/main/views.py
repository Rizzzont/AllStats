from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .total_profit import TotalProfit
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

    return render(request, "main/templates/not_main/index.html", {"total_profit": totalprofit})
def analytics(request):
    return render(request, ("main/templates/not_main/analytics.html"))


def recomendations(request):
    return render(request, ("main/templates/not_main/recomendations.html"))


def private_requests(request):
    return render(request, ("main/templates/not_main/private_requests.html"))

def register(request):
    return render(request, ("main/templates/not_main/register.html"))

def login(request):
    return render(request, ("main/templates/not_main/login.html"))

# class RegisterUser(DataMixin, CreateView):
#     form_class = UserCreationForm
#     template_name = "main/register.html"
#     success_url = reverse_lazy('login')
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title='Регистрация')
#         return dict(list(context.items())) + list(c_def.items())
