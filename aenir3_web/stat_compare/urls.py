from django.urls import path

from . import views

app_name = "stat_compare"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("edit/", views.edit_index, name="edit"),
    path("edit/<str:morph_id>", views.edit_morph),
    path("compare/", views.compare, name="compare"),
]
