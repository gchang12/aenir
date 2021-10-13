from importlib.machinery import PathFinder

from os import chdir, getcwd
from os.path import sep

def dir_switcher(name):
    aenir_loc=PathFinder()
    aenir_loc=aenir_loc.find_spec(name)
    aenir_loc=aenir_loc.origin
    aenir_loc=aenir_loc.split(sep)
    aenir_loc=sep.join(aenir_loc[:-1])
    chdir(aenir_loc)
    message=(
        '',\
        'The present working directory has been changed to:',\
        aenir_loc,\
        ''
        )
    message='\n'.join(message)
    print(message)
