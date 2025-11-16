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

![Logo](./logo.png)

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

## Usage

Let's begin by starting up an interactive Python shell.
We will start by importing the shortcut function `get_morph`.
```python
from aenir import get_morph
```

To create a virtual copy of a unit (i.e. a 'Morph'), bear in mind the following:

1. The name of the unit; this should have the [SerenesForest.Net](https://serenesforest.net/) spelling.
2. The number of the game the unit is from.

Let's say we want to get Roy's stats. Note that **Roy** is from FE**6**: The Sword of Seals.

```python
roy = get_morph(6, "Roy")
print(roy)
```

As you can see, these stats suck. Let's fix that; let's level him up to level twenty.

```python
num_levels = 20 - roy.current_lv
roy.level_up(num_levels)
print(roy)
```

That's better. But it's still not enough. Let's promote him.

```python
roy.promote()
```

For the fun of it, let's max him out.

```python
num_levels = 19 # because he starts out at level one again.
roy.level_up(num_levels)
print(roy)
```
 
Note that when initializing certain characters, like Rutger, extra initialization parameters will be needed. 

```python
rutger = get_morph(6, "Rutger", hard_mode=True)
larcei = get_morph(4, "Lakche", father="Lex")
lyn = get_morph(7, "Lyn", lyn_mode=True)
```

Compare characters by using the greater-than operator.

```python
roy > lyn
print(sum(roy > lyn))
```

## Limitations

Currently, this calculator works only for characters from:

4. Genealogy of the Holy War
5. Thracia 776
6. Sword of Seals
7. Blazing Blade
8. The Sacred Stones
9. Path of Radiance


# COMING SOON!

Combat simulation

<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
