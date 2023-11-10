from django.urls import path

from . import views

app_name = "stat_compare"

urlpatterns = [
    path("", views.StatCompare.index, name="index"),
    path("create/", views.StatCompare.create, name="create"),
    path("edit/", views.StatCompare.edit, name="edit"),
    path("compare/", views.StatCompare.compare, name="compare"),
]
