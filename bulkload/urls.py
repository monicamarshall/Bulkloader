from django.urls import path

from . import views

app_name = 'bulkload'

urlpatterns = [
    path('', views.index, name='index'),
    path('copy_from', views.copy_from, name='copy_from'),
    path('bulk_create', views.bulk_create, name='bulk_create'),
    #path('bulkload/<int:pk>', views.index, name='index'),
]

