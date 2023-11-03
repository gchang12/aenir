from django.urls import path

from . import views

app_name = "stat_compare"

urlpatterns = [
    path(f"{app_name}/", views.index, name="index"),
    path(f"{app_name}/create/", views.create, name="create"),
    path(f"{app_name}/edit/", views.edit, name="edit"),
    path(f"{app_name}/compare/", views.compare, name="compare"),
]
