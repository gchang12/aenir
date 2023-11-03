from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Root of application.
    """
    return render(request, "home/index.html", {})

def about(request):
    return HttpResponse("about")

def credits(request):
    return HttpResponse("credits")

def contact(request):
    return HttpResponse("contact")
