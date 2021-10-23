Be sure to download the directory_methods module so that this module can find the data files.

EXAMPLE OF USAGE
===
```python
rutger='6','Rutger'
rutger=Morph(\*rutger)
rutger.add\_hm\_bonus(chapter='')
rutger.level\_up(6)
rutger.promote(promo_path=0)
rutger.is\_capped(show\_df=True)
rutger.use\_stat\_booster('Energy Ring')
rutger.level\_up(18)
karel='6','Karel'
karel=Morph(\*karel)
comparison=rutger - karel
rutger()```
