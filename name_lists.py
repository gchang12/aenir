import pandas as pd
from aenir2.data_dict import read_stat_names
from os.path import sep
from os import walk
from aenir2.gender_dict import updated_name_for

def character_list(game,file_match='characters_base-stats'):
    data_dir='.','raw_data','fe'+game
    data_dir=sep.join(data_dir)
    compiled_names=()
    for root,folders,files in walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_match not in file:
                continue
            filename=data_dir,file
            filename=sep.join(filename)
            table=pd.read_csv(filename,index_col=0)
            name_list=table.index
            for name in name_list:
                if name in compiled_names:
                    continue
                if 'HM' in name:
                    continue
                if name == 'General':
                    continue
                if name == 'Nils':
                    continue
                compiled_names+=(name,)
    return compiled_names


def translated_character_list(game,raw_list=None,file_match='characters_base-stats'):
    if raw_list is None:
        raw_list=character_list(game,file_match=file_match)
    new_list=()
    for unit in raw_list:
        unit=updated_name_for(game,unit)
        new_list+=(unit,)
    return new_list


def fe4_child_list(get_father=False):
    game='4'
    filename='characters_growth-rates4.csv'
    kwargs={
        'game':game,\
        'file_match':filename
        }
    unit_list=character_list(**kwargs)
    kwargs['file_match']=filename.replace('4','1')
    parent_list=character_list(**kwargs)
    if get_father:
        yield 'Arden'
        condition = lambda unit: unit in parent_list
    else:
        condition = lambda unit: unit not in parent_list
    for unit in unit_list:
        if condition(unit):
            yield unit


def get_stat_names(game,stat_name=None):
    num_stats=read_stat_names(game)
    stats=()
    for stat in num_stats.keys():
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        if x not in stats:
            stats+=(x,)
    if stat_name is not None:
        return stats.index(stat_name)
    return stats



def read_class_names2(game,audit_name,match_name):
    name_file=r'fe'+game+'.csv'
    table='.','metadata','class_names',name_file
    table=sep.join(table)
    s=()
    audit_match=[audit_name,match_name]
    with open(table) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            s+=(line,)
    start=None
    stop=None
    for num,name in enumerate(s):
        if name == audit_match:
            start=num
        if not name[0] and start is not None:
            stop=num
            break
    if None in (start,stop):
        x={}
    else:
        x=dict(s[start+1:stop])
    return x

def game_title_dict(reverse=False):
    d={}
    d['Genealogy of the Holy War']='4'
    d['Thracia 776']='5'
    d['Binding Blade']='6'
    d['Blazing Sword']='7'
    d['The Sacred Stones']='8'
    d['Path of Radiance']='9'
    if reverse:
        t={}
        for key,val in d.items():
            t[val]=key
        return t
    return d


if __name__ == '__main__':
    k=4
    game=str(k)
    unit_list=fe4_child_list(True)
    #unit_list=translated_character_list(game,raw_list=unit_list)
    for unit in unit_list:
        print(unit)
