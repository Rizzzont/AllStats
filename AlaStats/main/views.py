from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

from main.functions import main_info, main_analytic
import pandas as pd
import tempfile

import os, zipfile, pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings

def upload_excel(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]

        temp_dir = os.path.join(settings.MEDIA_ROOT, "uploaded_excels")
        os.makedirs(temp_dir, exist_ok=True)

        excel_path = os.path.join(temp_dir, uploaded_file.name)
        with open(excel_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Чтение всех листов
        all_sheets = pd.read_excel(excel_path, sheet_name=None)  # словарь {имя_листа: DataFrame}

        # Сохраняем в pickle
        pickle_path = os.path.join(temp_dir, "data.pkl")
        all_sheets.to_pickle(pickle_path)

        request.session["data_path"] = pickle_path
        return redirect("main")  # или куда нужно

    return render(request, "main/upload.html")


def main(request):
    path = request.session.get("data_path")
    if not path or not os.path.exists(path):
        return render(request, "main/main.html", {
            "data_loaded": False
        })

    df = pd.read_pickle(path)

    summary = main_info(df)
    charts = main_analytic(df)

    return render(request, "main/main.html", {
        "profit": summary["profit"],
        "orders": summary["orders"],
        "rate": summary["rate"],
        "delivery_time": summary["delivery_time"],
        "chart_names": charts["chart_names"],
        "chart_sales": charts["chart_sales"],
        "chart_profit": charts["chart_profit"],
        "data_loaded": True
    })

def analytics(request):
    return render(request, "main/anal.html")


def recomendations(request):
    return render(request, "main/rec.html")


def private_requests(request):
    return render(request, "main/request.html")


def custom_404_view(request, exception):
    return render(request, 'main/404.html', status=404)

# Удаление данных
def delete_data(request):
    path = request.session.get("data_path")
    if path and os.path.exists(path):
        os.remove(path)
    request.session["data_path"] = None
    return redirect("main")
