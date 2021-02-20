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
        error_message='\n\nData files inaccessible. Please change directory to:\n\n%s'%aenir_loc
        class CwdError(Exception):
            def __init__(self,message):
                self.message=message
        if getcwd() != aenir_loc:
            raise CwdError(error_message)
