#   ***Provide docstrings for both classes

from aenir2.dracogate import Aenir
from aenir2.quintessence import Morph

#   Must change cwd to module directory

from os import chdir, getcwd
from os.path import sep
import aenir2

aenir_loc=aenir2.__file__
aenir_loc=aenir_loc.split(sep)
aenir_loc=sep.join(aenir_loc[:-1])

chdir(aenir_loc)

message=(
    'Current working directory has been changed to:',\
    aenir_loc,\
    'Data files now accessible by module.',\
    ''
    )
message='\n\n'.join(message)
print(message)

if __name__ == '__main__':
    repo='https://test.pypi.org/project/aenir2/'
