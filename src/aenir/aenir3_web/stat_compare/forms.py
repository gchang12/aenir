#!/usr/bin/python3
"""
"""

from django.forms import ModelForm

from .models import UnitSelect, GenealogyDad, LyndisLeague

class UnitSelectForm(ModelForm):
    class Meta:
        model = UnitSelect
        fields = ["game_num", "unit_name"]

class GenealogyDadForm(ModelForm):
    class Meta:
        model = GenealogyDad
        fields = ["father_name"]

class LyndisLeagueForm(ModelForm):
    class Meta:
        model = LyndisLeague
        fields = ["lyn_mode"]

if __name__ == '__main__':
    pass
