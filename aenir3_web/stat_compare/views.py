from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Contains a compendium of links to the application to access.
    """
    return render(request, "stat_compare/index.html", context={})

def create(request):
    # Implement global 'QUINTESSENCE' dict to create Morph object.
    # Show like a different set of controls every time data is sent.
    return render(request, "stat_compare/create.html", context={})

def edit(request):
    return render(request, "stat_compare/edit.html", context={})

def compare(request):
    return render(request, "stat_compare/compare.html", context={})
