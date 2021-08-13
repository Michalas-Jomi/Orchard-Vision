from django.urls import path

from . import views

app_name = "broker"
urlpatterns = [
    path('insert',       views.insert,      name="insert"),
    path('initinfo',     views.initinfo,    name="initinfo"),
    path('edit/type',    views.editType,    name="editType"),
    path('edit/variant', views.editVariant, name="editVariant"),
    path('edit/tree',    views.editTree,    name="editTree"),
]
