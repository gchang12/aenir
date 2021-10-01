HOW TO USE
===
rutger='6','Rutger'

rutger=Morph(\*rutger)

rutger.add_hm_bonus(chapter='')

rutger.level_up(6)

rutger.promote()

rutger.is_capped()

rutger.use_stat_booser('S/M')

rutger.level_up(18)

karel='6','Karel'

karel=Morph(\*karel)

comparison=rutger - karel

rutger()

REVISION NOTES
===
Trying to create a Morph object from somebody not in the game shows you a list of valid options

Trying to promote, boost stats, add HM/auto-level-bonuses with an invalid argument gives a list of valid options

Conditional returns statements are replaced by assertion statements

Methods that change unit stats among other things now return self

Fixed method to decrement Hugh's stats

Added Series option to is_capped method

Subtraction method has an extra line containing csum

Rewrote somethings in call method

Dummy-proofed the add_hm_bonus and add_auto_bonus methods with new is_clean method
