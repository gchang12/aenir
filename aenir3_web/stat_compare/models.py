from django.db import models

# Create your models here.

class FireEmblemGame(models.Model):
    game_num = models.PositiveSmallIntegerField(
        primary_key=True,
        )
    # to NOT be displayed
    game_name = models.CharField(
        unique=True,
        max_length=50,
        )
    display_name = models.CharField(
        unique=True,
        max_length=50,
        verbose_name="Game",
        )

class FireEmblemUnit(models.Model):
    game_num = models.ForeignKey(
        FireEmblemGame,
        on_delete=models.PROTECT,
        )
    unit_name = models.CharField(max_length=50)
    display_name = models.CharField(
        max_length=50,
        verbose_name="Unit",
        )
    # 7: lyn_mode: Lyn Mode units have this field set to a non-blank
    campaign = models.CharField(
        max_length=50,
        blank=True,
        choices=(
            ("lyn_mode", "Lyn Mode"),
            ("main", "Main"),
            ),
        verbose_name="Campaign",
        )
    # 4: father, child: children have this field set to a non-blank
    father_name = models.CharField(
        max_length=50,
        blank=True,
        choices=(
            ("Arden", "Arden"),
            ("Azel", "Azel"),
            ("Alec", "Alec"),
            ("Claude", "Claude"),
            ("Jamka", "Jamka"),
            ("Dew", "Dew"),
            ("Noish", "Noish"),
            ("Fin", "Fin"),
            ("Beowolf", "Beowolf"),
            ("Holyn", "Holyn"),
            ("Midayle", "Midayle"),
            ("Levin", "Levin"),
            ("Lex", "Lex"),
            ),
        verbose_name="Father",
        )
