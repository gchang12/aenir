#   Must change cwd to module directory

from importlib.machinery import PathFinder

from os import chdir, getcwd
from os.path import sep

def dir_switcher(mode):
    aenir_loc=PathFinder()
    aenir_loc=aenir_loc.find_spec('aenir2')
    aenir_loc=aenir_loc.origin
    aenir_loc=aenir_loc.split(sep)
    aenir_loc=sep.join(aenir_loc[:-1])

    if mode == 'chdir':
        chdir(aenir_loc)

    elif mode == 'assert':
        assert getcwd() == aenir_loc
