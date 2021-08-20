from django.urls import path

from . import views

app_name = "broker"
urlpatterns = [
    path('initinfo',     views.initinfo,    name="initinfo"),
    
    path('edit/type',     views.editType,    name="editType"),
    path('edit/variant',  views.editVariant, name="editVariant"),
    path('edit/tree',     views.editTree,    name="editTree"),
    path('edit/move/tree',views.editTreeMove,name="editTreeMove"),
    
    path('delete/type/<int:pk>',    views.deleteType,    name="deleteType"),
    path('delete/variant/<int:pk>', views.deleteVariant, name="deleteVariant"),
    path('delete/tree/<int:pk>',    views.deleteTree,    name="deleteTree"),

    path('new/type',    views.newType,    name="newType"),
    path('new/variant', views.newVariant, name="newVariant"),
    path('new/tree',    views.newTree,    name="newTree"),

    path('info/tree/<int:pk>', views.infoTree, name="infoTree"),
]
