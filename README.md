<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/aenir.svg?branch=main)](https://cirrus-ci.com/github/<USER>/aenir)
[![ReadTheDocs](https://readthedocs.org/projects/aenir/badge/?version=latest)](https://aenir.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/aenir/main.svg)](https://coveralls.io/r/<USER>/aenir)
[![PyPI-Server](https://img.shields.io/pypi/v/aenir.svg)](https://pypi.org/project/aenir/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/aenir.svg)](https://anaconda.org/conda-forge/aenir)
[![Monthly Downloads](https://pepy.tech/badge/aenir/month)](https://pepy.tech/project/aenir)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/aenir)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# aenir

## A Fire Emblem stats calculator
> This module lets you perform stat calculations for Fire Emblem units.

With this module, you can:
- Create a virtual copy of a unit and their stats.
- Level up that unit.
- Promote that unit.
- Compare one unit to another.
- And much more!

## Installation

To start, install `aenir`.
```bash
pip install aenir
```
Next, start up an interactive Python shell and import the shortcut function `get_morph`.
```python
from aenir.morph import get_morph
```

## Usage

Create a virtual copy of a unit (i.e. a 'Morph'), bearing in mind the following:

1. The name of the unit, per [SerenesForest.Net](https://serenesforest.net/).
2. The number of the game the unit is from.

Let's say we want to get Roy's stats. Note that Roy is from FE6: The Sword of Seals.

```python
roy = get_morph(6, "Roy")
# implicit: roy.__repr__()
roy
```

As you can see, these stats suck. Let's fix that; let's level him up to level twenty.

```python
num_levels = 20 - roy.current_lv
roy.level_up(num_levels)
# implicit: roy.__repr__()
roy
```

That's better. But it's still not enough. Let's promote him.

```python
roy.promote()
```

For the fun of it, let's max him out.

```python
num_levels = 19 # because he starts out at level one again.
roy.level_up(num_levels)
# implicit: roy.__repr__()
roy
```
 
Note that when initializing certain characters, like Rutger, extra initialization parameters will be needed. 

```python
rutger = get_morph(6, "Rutger", hard_mode=True)
larcei = get_morph(4, "Larcei", father="Lex")
lyn = get_morph(7, "Lyn", lyn_mode=True)
```

Compare characters by using the greater-than operator.

```python
roy > lyn
sum(roy > lyn)
```

## Limitations

Currently, this calculator works only for characters from:

4. Genealogy of the Holy War
5. Thracia 776
6. Sword of Seals
7. Blazing Blade
8. The Sacred Stones
9. Path of Radiance


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
