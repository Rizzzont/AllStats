from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
import pickle
from django.http import JsonResponse
import requests

from django.views.decorators.csrf import csrf_exempt

from main.functions import (main_info, main_analytic, designer_sum, designers_sum, category_sum,
                            categories_sum, good_sum, goods_sum, last)
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

        # Оптимизированное чтение
        xls = pd.ExcelFile(excel_path)
        all_sheets = {
            name: xls.parse(name)  # можно добавить usecols/nrows при необходимости
            for name in xls.sheet_names
        }

        pickle_path = os.path.join(temp_dir, "data.pkl")
        with open(pickle_path, "wb") as f:
            pickle.dump(all_sheets, f, protocol=pickle.HIGHEST_PROTOCOL)

        request.session["data_path"] = pickle_path
        return redirect("main")

    return render(request, "main/upload.html")

def main(request):
    path = request.session.get("data_path")
    if not path or not os.path.exists(path):
        return render(request, "main/main.html", {"data_loaded": False})

    with open(path, "rb") as f:
        sheet_dict = pickle.load(f)

    combined_df = pd.concat(sheet_dict.values(), ignore_index=True)
    summary = main_info(sheet_dict)
    charts = main_analytic(sheet_dict)

    return render(request, "main/main.html", {
        "profit": summary["profit"],
        "orders": summary["orders"],
        "rate": summary["rate"],
        "delivery_time": summary["delivery_time"],
        "chart_sales": charts["chart_sales"],
        "chart_profit": charts["chart_profit"],
        "chart_names": charts["chart_names"],
        "data_loaded": True
    })

# Загрузка данных из pkl файла
def load_sheet_dict(request):
    data_path = request.session.get("data_path")
    if not data_path or not os.path.exists(data_path):
        return {}
    with open(data_path, "rb") as f:
        return pickle.load(f)

# Главная страница аналитики
def analytics_view(request):
    return render(request, "main/anal.html")

# API для получения данных графика
def analytics_api(request):
    if request.method != "GET":
        return JsonResponse({"error": "Ожидался GET-запрос"}, status=400)

    func = request.GET.get("func")
    value = request.GET.get("value", "").strip()

    if func == "default" or not func:
        return JsonResponse({"labels": [], "values": []})

    # Загрузка данных из pickle
    data_path = request.session.get("data_path")
    if not data_path or not os.path.exists(data_path):
        return JsonResponse({"error": "Нет данных"}, status=400)

    with open(data_path, "rb") as f:
        sheet_dict = pickle.load(f)

    if not sheet_dict:
        return JsonResponse({"error": "Пустые данные"}, status=400)

    months = []

    for sheet_name, df in sheet_dict.items():
        months.append(sheet_name)

    try:
        if func == "chartDiz":
            values = designer_sum(sheet_dict, value)

        elif func == "chartCategory":
            values = category_sum(sheet_dict, value)

        elif func == "chartGood":
            values = good_sum(sheet_dict, value)

        elif func == "chartDizs":
            values = designers_sum(sheet_dict)
            print(values)

        elif func == "chartCategorys":
            values = categories_sum(sheet_dict)

        elif func == "chartGoods":
            values = goods_sum(sheet_dict)

        else:
            return JsonResponse({"error": "Неверный параметр func"}, status=400)

        print(values)
        return JsonResponse({"labels": months, "value_profit": values[0], "value_not_profit": values[1]})

    except Exception as e:
        return JsonResponse({"error": f"Ошибка обработки: {str(e)}"}, status=500)

def recomendations(request):
    return render(request, "main/rec.html")


def sells(request):
    # Загружаем Excel-файл
    data_path = request.session.get("data_path")
    if not data_path or not os.path.exists(data_path):
        return JsonResponse({"error": "Нет данных"}, status=400)

    with open(data_path, "rb") as f:
        xls = pickle.load(f)  # путь к файлу

    data = last(xls, month_choice="year")

    return render(request, "main/sells.html", {
        "data_json": data
    })


def custom_404_view(request, exception):
    return render(request, 'main/404.html', status=404)

# Удаление данных
def delete_data(request):
    path = request.session.get("data_path")
    if path and os.path.exists(path):
        os.remove(path)
    request.session["data_path"] = None
    return redirect("main")


GPT_LOCAL_API_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "google/gemma-3-1b"

@csrf_exempt
def freegpt_proxy(request):
    if request.method == "POST":
        body = json.loads(request.body)
        prompt = body.get("prompt", "")
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        try:
            resp = requests.post(GPT_LOCAL_API_URL, json=payload, timeout=120)
            data = resp.json()
            answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Ошибка: пустой ответ")
            print(answer)
            return JsonResponse({"answer": answer})
        except Exception as e:
            return JsonResponse({"answer": f"Ошибка при обращении к LM Studio: {e}"})
    return JsonResponse({"error": "Only POST allowed"}, status=405)

