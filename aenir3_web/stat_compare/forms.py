#!/usr/bin/python3
"""
"""

from .models import (
    FireEmblemGame, # game_num, game_name, display_name
    FireEmblemUnit # game_num, unit_name, display_name, campaign, father_name
    )
from django.forms import ModelForm, Select

GAMESELECT_CHOICES = (
    (fe_game.game_num, fe_game.display_name) for fe_game in FireEmblemGame.objects.all()
    )

UNITSELECT_CHOICES = (
    (fe_unit.unit_name, fe_unit.display_name) for fe_unit in FireEmblemUnit.objects.all()
    )

def get_UNITSELECT_CHOICES(game_num):
    UNITSELECT_CHOICES = (
        (fe_unit.unit_name, fe_unit.display_name) for fe_unit in FireEmblemUnit.objects.filter(game_num=game_num)
        )
    return UNITSELECT_CHOICES

class GameSelect(ModelForm):
    class Meta:
        model = FireEmblemGame
        fields = ["display_name"]
        widgets = {
                "display_name": Select(choices=GAMESELECT_CHOICES),
                }


class UnitSelect(ModelForm):
    class Meta:
        model = FireEmblemUnit
        fields = ["display_name"]
        widgets = {
                "display_name": Select(choices=UNITSELECT_CHOICES),
                }



if __name__ == '__main__':
    pass
