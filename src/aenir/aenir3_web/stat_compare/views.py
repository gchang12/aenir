#!/usr/bin/python3
"""
"""

from django.shortcuts import render

from .forms import (
    UnitSelectForm,
    GenealogyDadForm,
    LyndisLeagueForm,
)
from .models import (
    DragonsGate,
    LyndisLeague,
    GenealogyKid,
    GenealogyDad,
    FireEmblemUnit,
)
import aenir.morph


class StatCompareViews:
    """
    """

    # for use in creating Morphs
    QUINTESSENCE = {}

    # for use in Morph methods
    datadir_root = "./stat_compare/static/stat_compare/data/"

    # for use in rendering the web page
    about_unit = {}
    unit_history = {}

    @classmethod
    def create_confirm(cls, request):
        pass

    @classmethod
    def create_extra(cls, request):
        """
        For:
        - FE6,7,8: Hard Mode
        - FE7: Lyndis League
        - FE4: Kids
        """
        pass

    @classmethod
    def _create_new_morph(cls, request):
        # make and save Morph
        game_num = cls.QUINTESSENCE.pop("game_num")
        new_morph = getattr(aenir.morph, "Morph" + str(game_num))(**cls.QUINTESSENCE)
        DragonsGate(
            user=request.user,
            game_num=game_num,
            unit_name=cls.QUINTESSENCE["unit_name"],
            current_clstype=new_morph.current_clstype,
            current_cls=new_morph.current_cls,
            current_lv=new_morph.current_lv,
            promo_cls=new_morph.promo_cls,
            bases=new_morph.bases.to_json(),
            growths=new_morph.growths.to_json(),
            comparison_labels=new_morph.comparison_labels,
        ).save()
        # clear QUINTESSENCE
        cls.QUINTESSENCE.clear()
        # redirect to home
        context = {"view_name": ""}
        return render(request, "stat_compare/index.html", context=context)

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
        # 0: (GET request sent)
        # 1: game_num, unit_name
        # 2: select either campaign or dad
        # 3: *
        context = {"view_name": "Create"}
        if request.method == "POST":
            # 1
            try:
                game_num = int(request.POST["game_num"])
                unit_name = FireEmblemUnit.objects.get(pk=int(request.POST["unit_name"][0]))
                QUINTESSENCE.update( {
                    "game_num": game_num,
                    "unit_name": unit_name,
                    }
                )
            except KeyError:
                pass
            # 2
            if "lyn_mode" in request.POST:
                lyn_mode = bool(request.POST["lyn_mode"])
                QUINTESSENCE.update({"lyn_mode": lyn_mode})
                return cls._create_new_morph(cls, request)
            # 2
            elif "father_name" in request.POST:
                father_name = request.POST["father_name"]
                QUINTESSENCE.update({"father_name": father_name})
                return cls._create_new_morph(cls, request)
            else:
                # 1
                skip_fatherselect = False
                try:
                    GenealogyKid.objects.get(unit_name=unit_name)
                    context.update({"form": GenealogyDadForm()})
                except GenealogyKid.DoesNotExist:
                    skip_fatherselect = True
                # 1
                skip_campaignselect = False
                try:
                    LyndisLeague.objects.get(unit_name=unit_name)
                    context.update({"form": LyndisLeagueForm()})
                except LyndisLeague.DoesNotExist:
                    skip_campaignselect = True
                if skip_fatherselect and skip_campaignselect:
                    return cls._create_new_morph(cls, request)
        # 0
        else:
            context.update({"form": UnitSelectForm()})
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
