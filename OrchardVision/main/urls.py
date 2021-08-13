from django.urls import path, re_path

from . import views

app_name = "main"
urlpatterns = [
    path('type/<int:pk>',         views.TypeView.as_view(),        name="type"),
    path('type/edit/<int:pk>',    views.TypeEditView.as_view(),    name="typeEdit"),
    path('variant/<int:pk>',      views.VariantView.as_view(),     name="variant"),
    path('variant/edit/<int:pk>', views.VariantEditView.as_view(), name="variantEdit"),
    re_path(r'(index(\.html)?)?', views.IndexView.as_view(),       name="index"),
]
