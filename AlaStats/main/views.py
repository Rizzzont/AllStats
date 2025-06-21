from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

from main.functions import main_info, analytic
import pandas as pd
import tempfile

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
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        df = pd.read_excel(uploaded_file, sheet_name='Товары')

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        df.to_pickle(temp.name)

        request.session['data_path'] = temp.name
        print("На вкладку main")
        return redirect("main")

    print("На вкладку upload")
    return render(request, "main/upload.html")


@group_required('Сотрудник')
def main(request):
    path = request.session.get('data_path')
    if not path or not os.path.exists(path):
        return render(request, "main/NoData.html")

    df = pd.read_pickle(path)
    info = main_info(df)

    main_data = analytic(df)
    print(main_data)
    context = {
        **info,
        **main_data
    }

    return render(request, "main/main.html", context)


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
