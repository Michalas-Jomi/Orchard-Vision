from django.urls import path

from . import views

app_name = "orchardMap"
urlpatterns = [
    path('treeInfo/<int:tree>/', views.TreeInfo.as_view(), name="treeInfo"),
    path('', views.MapView.as_view(), name="map"),
]
