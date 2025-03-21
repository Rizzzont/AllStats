from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render

from main.total_profit import TotalProfit
import pandas as pd

ROLES = ['Сотрудник', 'Директор']


def group_required(min_group):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user_groups = request.user.groups.values_list('name', flat=True)

            if any(group in ROLES[ROLES.index(min_group):] for group in user_groups):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "main/сonfirmation.html")

        return _wrapped_view

    return decorator


@group_required('Сотрудник')
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

    return render(request, "main/main.html", {"total_profit": totalprofit})


@group_required('Сотрудник')
def analytics(request):
    return render(request, "main/anal.html")


@group_required('Сотрудник')
def recomendations(request):
    return render(request, "main/recomendations.html")


@group_required("Сотрудник")
def private_requests(request):
    return render(request, "main/private_requests.html")


def custom_404_view(request, exception):
    return render(request, 'main/404.html', status=404)
