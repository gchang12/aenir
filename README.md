from aenir2 import Morph

game='6' # for Binding Blade, the game Roy appears in
unit='Roy' # because he's our boy

x=Morph(game,unit)

x.level_up(19) # Adding nineteen levels to Roy; stats determined by character growths
x.promote() # Promoting Roy to Master Lord
x.level_up(19) # Adding nineteen more levels

x() # Compare your stats to 20/20 Roy via native input function
