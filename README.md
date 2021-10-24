Be sure to download the directory_methods module so that this module can find the data files.

TYPICAL USAGE
===
```python
rutger='6','Rutger'
rutger=Morph(*rutger)
rutger.add_hm_bonus(chapter='')
rutger.level_up(6)
rutger.promote(promo_path=0)
rutger.is_capped(show_df=True)
rutger.use_stat_booster('Energy Ring')
rutger.level_up(18)
karel='6','Karel'
karel=Morph(*karel)
comparison=rutger - karel
rutger()```
