How to perform stat comparison
===
# Example: 20/20 Roy


from aenir2 import Morph

game='6'
unit='Roy'

x=Morph(game,unit)

x.level_up(19)
x.promote()
x.level_up(19)

x()
