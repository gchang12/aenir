from django.urls import path

from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("credits/", views.credits, name="credits"),
    path("contact/", views.contact, name="contact"),
]
