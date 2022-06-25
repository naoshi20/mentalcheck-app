from django.urls import path

from . import views
from .views import defore_index

app_name = 'check'
urlpatterns = [
    path('before/', defore_index, name='beforeIndex'),
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:slug>/', views.ConstructIndexView.as_view(), name='construct_index'),
    path('stressqol/results/latest/', views.LatestStressSQLResultView.as_view(),
         name='stress_qol_result_latest'),
]