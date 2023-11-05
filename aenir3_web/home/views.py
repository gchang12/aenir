from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Root of application.
    """
    return render(request, "home/index.html", {})

def about(request):
    return render(request, "home/about.html", {})

def credits(request):
    return render(request, "home/credits.html", {})

def contact(request):
    return render(request, "home/contact.html", {})
