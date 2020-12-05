from aenir2.dracogate import Aenir
from aenir2.quintessence import Morph
from aenir2.data_fetcher import save_raw_data

from os import getcwd
from os.path import exists, sep

shell_dir=getcwd()
metadata_dir=sep.join((shell_dir,'metadata'))

if not exists(metadata_dir):
    message='Please move metadata folder to %s'%shell_dir
    print(message)
else:
    raw_data_dir=sep.join((shell_dir,'raw_data'))
    if not exists(raw_data_dir):
        x=input('Data folder will be saved to cwd. Proceed? (y/n)')
        if x == 'y':
            save_raw_data()

if __name__ == '__main__':
    Aenir()()
