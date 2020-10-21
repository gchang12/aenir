from os.path import exists,sep
from os import mkdir

from requests import get
from bs4 import BeautifulSoup

url='https://serenesforest.net'

def to_dir(name):
    return '.'+sep+name

cache=to_dir('raw_data')
metadata=to_dir('metadata')

if not exists(cache):
    mkdir(cache)

def paths_for(game):
    global url
    path_list=sep.join([metadata,r'compile-paths.txt'])
    t=tuple()
    with open(path_list) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            if line[0] != game:
                continue
            num=line[0]
            title=line[1]
            x='classes'
            y='characters'
            cs_start=line.index(x)
            ch_start=line.index(y)
            ch=line[ch_start+1:cs_start]
            cs=line[cs_start+1:]
            for sec in (ch,cs):
                if sec == ch:
                    portal=y
                elif sec == cs:
                    portal=x
                for s in sec:
                    parts=(url,title,portal,s)
                    path='/'.join(parts)
                    t+=(path,)
    return t


def html_soups(game):
    paths=paths_for(game)
    soups=tuple()
    if game == '9':
        parser='html5lib'
    else:
        parser='html.parser'
    for path in paths:
        bs=BeautifulSoup(get(path).text,parser)
        soups+=(bs,)
    return soups


def row_fetcher(table):
    data=tuple()
    got_header=False
    for row in table.find_all(name='tr'):
        cells=tuple()
        for t in row.find_all(name='td'):
            cells+=(t.text,)
        if not got_header:
            for h in row.find_all(name='th'):
                cells+=(h.text,)
            got_header=True
        if cells:
            data+=(cells,)
    return list(data)


def table_fetcher(game):
    soups=html_soups(game)
    contents={}
    sites=paths_for(game)
    for soup,site in zip(soups,sites):
        tables=soup.find_all(name='table')
        site=site.split('/')
        site=site[-2:]
        path='_'.join(site)
        if len(tables) > 1:
            n=1
            for table in tables:
                contents[path+str(n)]=row_fetcher(table)
                n+=1
        else:
            contents[path]=row_fetcher(soup.table)
    return contents


def stat_recorder(game):
    tables=table_fetcher(game)
    import pandas as pd
    folder='fe'+game
    full_dir=cache+sep+folder
    if not exists(full_dir):
        mkdir(full_dir)
    for name in tables.keys():
        file=sep.join([cache,folder,name+'.csv'])
        x=pd.DataFrame(tables[name])
        x.to_csv(file,index=False,header=False)

if __name__=='__main__':
    for k in range(4,10):
        game=str(k)
        stat_recorder(game)
