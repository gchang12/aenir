HOW TO USE
===
ourboy='6','Roy'


ourboy=Morph(\*ourboy)

ourboy.level_up(19)

outboy.promote()

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
