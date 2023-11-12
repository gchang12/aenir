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
from .forms import GameSelect
from aenir.morph import (
        #BaseMorph,
        Morph4, Morph5, Morph6, Morph7, Morph8, Morph9
        )

# Create your views here.

class StatCompare:
    """
    """
    QUINTESSENCE = OrderedDict()

    # for use in Morph methods
    DATADIR_ROOT = "./stat_compare/static/stat_compare/data/"

    @classmethod
    def index(cls, request):
        """
        Contains a compendium of links to the application to access.
        """
        context = {"view_name": ""}
        return render(request, "stat_compare/index.html", context=context)

    @classmethod
    def create(cls, request):
        """
        """
        # Implement global 'QUINTESSENCE' dict to create Morph object.
        # Show like a different set of controls every time data is sent.
        context = {"view_name": "Create"}
        form = GameSelect()
        context.update({"form": form})
        print(cls.QUINTESSENCE)
        if request.method == "POST":
            game_num = int(request.POST["display_name"])
            cls.QUINTESSENCE.update({"game_num": game_num})
        return render(request, "stat_compare/create.html", context=context)

    @classmethod
    def edit(cls, request):
        """
        """
        context = {"view_name": "Edit"}
        return render(request, "stat_compare/edit.html", context=context)

    @classmethod
    def compare(cls, request):
        """
        """
        context = {"view_name": "Compare"}
        return render(request, "stat_compare/compare.html", context=context)
