from aenir2.data_fetcher import save_raw_data

from os import getcwd
from os.path import exists, sep

shell_dir=getcwd()
metadata_dir=sep.join((shell_dir,'metadata'))
raw_data_dir=sep.join((shell_dir,'raw_data'))

if not exists(metadata_dir):
    message='Please move \"metadata\" folder to:\n\n%s'%shell_dir
    print(message)
else:
    if not exists(raw_data_dir):
        message(
            'SerenesForest data will be scraped and saved to:',\
            shell_dir,
            'Proceed? (y/n)'
            )
        message='\n\n'.join(message)
        x=input(message)
        if x == 'y':
            save_raw_data()
            message='SerenesForest data successfully scraped and saved!'
        else:
            message=(
                'Please insert the \"raw_data\" folder into %s'%shell_dir,\
                'Otherwise, the Aenir class will not function properly.'
                )
            message='\n\n'.join(message)
        print(message)

if __name__ == '__main__':
    x=4
