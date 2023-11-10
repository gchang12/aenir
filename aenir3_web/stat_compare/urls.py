from django.urls import path

from . import views

app_name = "stat_compare"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("edit/", views.edit, name="edit"),
    path("compare/", views.compare, name="compare"),
]
