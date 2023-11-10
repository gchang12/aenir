#!/usr/bin/python3
"""
"""

from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import render

from .models import (
    FireEmblemGame, # game_num, game_name, display_name
    FireEmblemUnit # game_num, unit_name, display_name, campaign, father_name
    )
from aenir.morph import (
        BaseMorph,
        Morph4, Morph5, Morph6, Morph7, Morph8, Morph9
        )

# Create your views here.

class StatCompare:
    """
    """
    QUINTESSENCE = OrderedDict()

    # for use in Morph methods
    datadir_root = "./stat_compare/static/stat_compare/data/"

    @classmethod
    def index(cls, request):
        """
        Contains a compendium of links to the application to access.
        """
        import os
        print(os.getcwd())
        #BaseMorph(4, cls.datadir_root)
        sigurd = Morph4("Sigurd", datadir_root=cls.datadir_root)
        return render(request, "stat_compare/index.html", context={})#{"view_name": sigurd.unit_name })

    @classmethod
    def create(cls, request):
        """
        """
        # Implement global 'QUINTESSENCE' dict to create Morph object.
        # Show like a different set of controls every time data is sent.
        return render(request, "stat_compare/create.html", context={})

    @classmethod
    def edit(cls, request):
        """
        """
        return render(request, "stat_compare/edit.html", context={})

    @classmethod
    def compare(cls, request):
        """
        """
        return render(request, "stat_compare/compare.html", context={})
