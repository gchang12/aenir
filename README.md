HOW TO USE
==========
```python
# create Morph object
from aenir.morph import Morph6
roy = Morph6("Roy")
# specify target level
roy.level_up(20)
# cap stats wrt unit's maximum-stats for their class
roy.cap_stats()
# promote unit
roy.promote()
```

```python
# create Morph objects to compare stats
from aenir.morph import Morph6
# create maxed-out Allen
allen = Morph6("Allen")
allen.level_up(20)
allen.promote()
allen.level_up(20)
allen.cap_stats()
# create maxed-out Lance
lance = Morph6("Lance")
lance.level_up(20)
lance.promote()
lance.level_up(20)
lance.cap_stats()
# compare stats
allen < lance
```

```python
# create FE4 kid Morph
lakche = Morph4("Lakche", "Lex")
lakche.level_up(20)
lakche.promote()
lakche.level_up(30)
lakche.cap_stats()
```

```python
# train virtual Ross
ross = Morph8("Ross")
ross.level_up(10)
ross.promo_cls = "Pirate"
ross.promote()
ross.level_up(20)
ross.promo_cls = "Berserker"
ross.promote()
ross.level_up(20)
ross.cap_stats()
```

```python
# fun with Lara
lara = Morph5("Lara")
# promote to Thief Fighter
lara.promo_cls = "Thief Fighter"
lara.level_up(10)
lara.promote()
# promote to Dancer
lara.promo_cls = "Dancer"
lara.promote()
# promote to Thief Fighter
lara.promo_cls = "Thief Fighter"
lara.level_up(10)
lara.promote()
```

# https://pyscaffold.org/en/stable/features.html#package-and-files-data
# - where to put this code?
# Note to self: Segregate tests into unit and integration folders

Consider refactoring st Morph instance hasn't much luggage
- character-{bases,growths}
Consider polars over pandas for Morph functionality.
- requires heavy refactoring perhaps
