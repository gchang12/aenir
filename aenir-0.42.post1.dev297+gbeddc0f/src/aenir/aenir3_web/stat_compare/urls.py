from django.urls import path

from .views import StatCompareViews

app_name = "stat_compare"

urlpatterns = [
    path("", StatCompareViews.index, name="index"),
    path("create/", StatCompareViews.create, name="create"),
    path("edit/", StatCompareViews.edit, name="edit"),
    path("compare/", StatCompareViews.compare, name="compare"),
]
