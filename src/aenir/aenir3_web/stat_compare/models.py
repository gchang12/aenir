from django.db import models
from smart_selects.db_fields import ChainedForeignKey


class FireEmblemGame(models.Model):
    game_num = models.PositiveSmallIntegerField(
        primary_key=True,
        )
    # to NOT be displayed
    game_name = models.CharField(
        unique=True,
        max_length=50,
        )
    display_gamename = models.CharField(
        unique=True,
        max_length=50,
        verbose_name="Game",
        )
    def __str__(self):
        return self.display_gamename


class FireEmblemUnit(models.Model):
    game_num = models.ForeignKey(
        FireEmblemGame,
        on_delete=models.PROTECT,
        )
    unit_name = models.CharField(
        max_length=50,
        #verbose_name="Unit",
        )
    display_unitname = models.CharField(
        max_length=50,
        #verbose_name="Unit",
        )
    def __str__(self):
        return self.display_unitname
        #return str(self.game_num.game_num) + ": " + self.display_unitname


class UnitSelect(models.Model):
    game_num = models.ForeignKey(
        FireEmblemGame,
        on_delete=models.PROTECT,
        verbose_name="Game",
        )
    unit_name = ChainedForeignKey(
        FireEmblemUnit,
        chained_field="game_num",
        chained_model_field="game_num",
        show_all=False,
        sort=False,
        verbose_name="Unit",
        )
    def __str__(self):
        return str(self.game_num) + ": " + self.unit_name.display_unitname

class DragonsGate(models.Model):
    game_num = models.PositiveSmallIntegerField(default=0)
    unit_name = models.CharField(max_length=50, default="")
    current_clstype = models.CharField(max_length=50, default="")
    current_cls = models.CharField(max_length=50, default="")
    current_lv = models.PositiveSmallIntegerField(default=0)
    promo_cls = models.CharField(max_length=50, default="")
    bases = models.JSONField(default=dict)
    growths = models.JSONField(default=dict)
    comparison_labels = models.JSONField(default=dict)
    history = models.JSONField(default=list)

# not to be used in forms and so forth

class LyndisLeague(models.Model):
    #game_num = models.PositiveSmallIntegerField( #primary_key=True,)
    unit_name = models.CharField(
        max_length=50,
        primary_key=True,
        )
    display_unitname = models.CharField(
        max_length=50,
        )
    lyn_mode = models.BooleanField(
        default=False,
        verbose_name="Campaign",
        choices=[
            (False, "Main"),
            (True, "Tutorial"),
            ]
        )
    def __str__(self):
        return self.display_unitname

class GenealogyKid(models.Model):
    #game_num = models.PositiveSmallIntegerField( #primary_key=True,)
    unit_name = models.CharField(
        max_length=50,
        primary_key=True,
        )
    display_unitname = models.CharField(
        max_length=50,
        )
    def __str__(self):
        return self.display_unitname

class GenealogyDad(models.Model):
    #game_num = models.PositiveSmallIntegerField( #primary_key=True,)
    father_name = models.CharField(
        max_length=50,
        primary_key=True,
        )
    display_fathername = models.CharField(
        max_length=50,
        )
    def __str__(self):
        return self.display_fathername

