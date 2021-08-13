from django.urls import path

from . import views

app_name = "broker"
urlpatterns = [
    path('insert', views.insert, name="insert"),
    path('initinfo', views.initinfo, name="initinfo"),
    path('editTree', views.editTree, name="editTree"),
]
