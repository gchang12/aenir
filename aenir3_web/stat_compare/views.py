#!/usr/bin/python3
"""
"""

from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import render
# to fix some weirdness with POST data handling
from django.utils.datastructures import MultiValueDictKeyError

from .models import (
    FireEmblemGame, # game_num, game_name, display_name
    FireEmblemUnit # game_num, unit_name, display_name, campaign, father_name
    )
from .forms import GameSelect, UnitSelect, get_UNITSELECT_CHOICES
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
    
    DISPLAY_DICT = {
            'game_num': "Game",
            'unit_name': "Unit",
            }

    # for use in rendering
    ABOUT_TABLE = []

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
        forms_to_fill = OrderedDict()
        forms_to_fill.update({"game_num": GameSelect}
            )
        forms_to_fill.update({"unit_name": UnitSelect})
        for morph_field in forms_to_fill:
            if morph_field in cls.QUINTESSENCE:
                continue
            break
        form = forms_to_fill[morph_field]()
        context.update({"form": form})
        context.update({"about_table": cls.ABOUT_TABLE})
        if request.method == "POST":
            morph_data = request.POST["display_name"]
            if morph_data.isnumeric():
                morph_data = int(morph_data)
            cls.QUINTESSENCE.update({morph_field: morph_data})
            if morph_field == "game_num":
                morph_data = FireEmblemGame.objects.get(game_num=morph_data).display_name
            cls.ABOUT_TABLE.append(
                    (cls.DISPLAY_DICT[morph_field], morph_data)
                    )
        elif request.method == "GET":
            cls.QUINTESSENCE.clear()
        else:
            # TODO: What do I do if the user makes anything other than a POST or GET request?
            raise Exception
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
