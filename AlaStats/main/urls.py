from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_excel, name='upload'),
    path('main/', views.main, name="main"),
    path('recomendations/', views.recomendations, name="recomendations"),
    path('sells/', views.sells, name="sells"),
    path('delete/', views.delete_data, name='delete_data'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
    path("ai_freegpt/", views.freegpt_proxy, name="ai_freegpt"),
    path("information/", views.information, name="information"),
    path('api/autocomplete_goods/', views.autocomplete_goods, name='autocomplete_goods'),
]

handler404 = views.custom_404_view