from django.urls import path, re_path

from . import views

app_name = "main"
urlpatterns = [
    path('type/<int:pk>',    views.TypeView.as_view(),        name="type"),
    path('variant/<int:pk>', views.VariantView.as_view(),     name="variant"),
    path('harvestTime/info', views.HarvestTimesView.as_view(),name="harvestTimes"),

    path('type/edit/<int:pk>',        views.TypeEditView.as_view(),       name="typeEdit"),
    path('variant/edit/<int:pk>',     views.VariantEditView.as_view(),    name="variantEdit"),
    path('harvestTime/edit/<int:pk>', views.HarvestTimeEditView.as_view(),name="harvestTimeEdit"),
    
    path('type/new',        views.TypeNewView.as_view(),        name="typeNew"),
    path('variant/new',     views.VariantNewView.as_view(),     name="variantNew"),
    path('harvestTime/new', views.HarvestTimeNewView.as_view(), name="newHarvestTime"),
    
    path('index', views.IndexView.as_view(), name="index"),
]
