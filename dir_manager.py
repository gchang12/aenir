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
        if aenir_loc == getcwd():
            return
        error_message=(
            '',
            'Data files inaccessible. Change directory to:',\
            aenir_loc,\
            '? (Y/N)',\
            ''
            )
        error_message='\n\n'.join(error_message)
        answer=''
        while answer not in ('y','n'):
            answer=input(error_message)
            answer=answer.lower()
        if answer == 'y':
            chdir(aenir_loc)
        elif answer == 'n':
            raise Exception
