#   ***Provide docstrings for both classes

from aenir2.dracogate import Aenir
from aenir2.quintessence import Morph

#   Must change cwd to module directory

from importlib.machinery import PathFinder

from os import chdir
from os.path import sep

aenir_loc=PathFinder()
aenir_loc=aenir_loc.find_spec('aenir2')
aenir_loc=aenir_loc.origin
aenir_loc=aenir_loc.split(sep)
aenir_loc=sep.join(aenir_loc[:-1])

chdir(aenir_loc)

#   Print notification of directory change

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
