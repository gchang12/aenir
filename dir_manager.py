from importlib.machinery import PathFinder

from os import chdir, getcwd
from os.path import sep

def dir_switcher(name,notify=False):
    aenir_loc=PathFinder()
    aenir_loc=aenir_loc.find_spec(name)
    aenir_loc=aenir_loc.origin
    aenir_loc=aenir_loc.split(sep)
    aenir_loc=sep.join(aenir_loc[:-1])
    chdir(aenir_loc)
    if notify:
        message=(
            'The present working directory has been changed to:',\
            aenir_loc,\
            'Data files are now accessible.'
            )
        new_message=['']
        for text in message:
            new_message.append(text)
            new_message.append('')
        message='\n'.join(new_message)
        print(message)
