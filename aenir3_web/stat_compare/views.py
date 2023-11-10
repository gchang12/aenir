from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

class StatCompare:
    QUINTESSENCE = OrderedDict()

    @classmethod
    def index(cls, request):
        """
        Contains a compendium of links to the application to access.
        """
        return render(request, "stat_compare/index.html", context={})

    @classmethod
    def create(cls, request):
        # Implement global 'QUINTESSENCE' dict to create Morph object.
        # Show like a different set of controls every time data is sent.
        return render(request, "stat_compare/create.html", context={})

    @classmethod
    def edit(cls, request):
        return render(request, "stat_compare/edit.html", context={})

    @classmethod
    def compare(cls, request):
        return render(request, "stat_compare/compare.html", context={})
