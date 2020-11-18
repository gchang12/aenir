from os.path import exists,sep
from os import mkdir
import pandas as pd
from requests import get
from bs4 import BeautifulSoup

url='https://serenesforest.net'

def path_to_directory(name):
    return '.'+sep+name

cache_folder=path_to_directory('raw_data')
metadata=path_to_directory('metadata')

if not exists(cache_folder):
    mkdir(cache_folder)


def paths_for(game):
    global url
    path_list=sep.join(['.',r'data-locations.txt'])
    with open(path_list) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            if line[0] != game:
                continue
            num=line[0]
            title=line[1]
            class_text='classes'
            character_text='characters'
            class_loc=line.index(class_text)
            character_loc=line.index(character_text)
            characters=line[character_loc+1:class_loc]
            classes=line[class_loc+1:]
            for section in (characters,classes):
                if section == characters:
                    portal=character_text
                elif section == classes:
                    portal=class_text
                for s in section:
                    path=(url,title,portal,s)
                    path='/'.join(path)
                    yield path


def soups_for(game):
    paths=paths_for(game)
    if game == '9':
        parser='html5lib'
    else:
        parser='html.parser'
    for path in paths:
        bs=BeautifulSoup(get(path).text,parser)
        yield bs


def rows_for(table):
    rows=tuple()
    got_header=False
    for row in table.find_all(name='tr'):
        cells=tuple()
        for t in row.find_all(name='td'):
            tdtxt=t.text
            tdtxt=tdtxt.replace('*','')
            tdtxt=tdtxt.strip()
            cells+=(tdtxt,)
        if not got_header:
            for h in row.find_all(name='th'):
                thtxt=h.text
                cells+=(thtxt,)
            got_header=True
        if cells:
            rows+=(cells,)
    return rows


def tables_for(game):
    soups=soups_for(game)
    table_dict={}
    sites=paths_for(game)
    for soup,site in zip(soups,sites):
        tables=soup.find_all(name='table')
        site=site.split('/')
        site=site[-2:]
        path='_'.join(site)
        if len(tables) > 1:
            for n, table in enumerate(tables,start=1):
                table_dict[path+str(n)]=rows_for(table)
        else:
            table_dict[path]=rows_for(soup.table)
    return table_dict


def save_stats(game):
    tables=tables_for(game)
    folder='fe'+game
    full_dir=cache_folder+sep+folder
    if not exists(full_dir):
        mkdir(full_dir)
    for name,table in tables.items():
        file=sep.join([cache_folder,folder,name+'.csv'])
        data=pd.DataFrame(table)
        data.to_csv(file,index=False,header=False)


if __name__=='__main__':
    save_stats('8')
