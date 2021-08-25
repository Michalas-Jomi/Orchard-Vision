from django.urls import path

from . import views

app_name = "orchardMap"
urlpatterns = [
    path('data/', views.Data.as_view(), name="data"),
    path('newTree/', views.TreeNew.as_view(), name="newTree"),
    path('treeInfo/<int:pk>/', views.TreeInfo.as_view(), name="treeInfo"),
    path('', views.MapView.as_view(), name="map"),
]
