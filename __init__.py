from aenir2.dracogate import Aenir
from aenir2.quintessence import Morph
from aenir2.data_fetcher import save_raw_data

from os import getcwd
from os.path import exists, sep

shell_dir=getcwd()
metadata_dir=sep.join((shell_dir,'metadata'))

if not exists(metadata_dir):
    message='Please move \"metadata\" folder to:\n\n%s'%shell_dir
    print(message)
else:
    raw_data_dir=sep.join((shell_dir,'raw_data'))
    if not exists(raw_data_dir):
        message(
            '\"raw_data\" folder will be saved to:',\
            shell_dir,
            'Proceed? (y/n)'
            )
        message='\n\n'.join(message)
        x=input(message)
        if x == 'y':
            save_raw_data()
        else:
            message=(
                'Aenir class will not function properly.',\
                'Import this module again if you change your mind.'
                )
            message='\n\n'.join(message)
            print(message)

if __name__ == '__main__':
    Aenir()()
