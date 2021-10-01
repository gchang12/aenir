HOW TO USE
===
rutger='6','Rutger'

rutger=Morph(\*rutger)

rutger.add_hm_bonus(chapter='')

rutger.level_up(6)

rutger.promote(promo_path=0)

rutger.is_capped(show_series=True)

rutger.use_stat_booster('Energy Ring')

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

Fixed the use_stat_booster method to take item-names as arguments, instead of stat names

Added Knoll's "HM" bonuses.

Syntax corrections for conditioning on numpy arrays

Method \'decline_hugh\' corrected so that Hugh does not have negative stats

Methds add_hm_bonus and add_auto_bonus corrected for Gonzales

New assertions added in place of if statements

No more auto-level up for promote method

Cleaned code for more conciseness

Allowed user to input updated names for units
