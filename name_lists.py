import pandas as pd
from aenir2.data_dict import read_stat_names
from os.path import sep
from os import walk
from aenir2.gender_dict import updated_name_for

def game_title_dict(reverse=False):
    title_file='.','metadata',r'game-titles.csv'
    title_file=sep.join(title_file)
    titles={}
    with open(title_file) as rfile:
        for line in rfile.readlines():
            line=line.strip()
            line=line.split(',')
            name=line[0]
            num=line[1]
            titles[name]=num
    if reverse:
        t={}
        for key,val in titles.items():
            t[val]=key
        return t
    return d

def character_list(game,file_match='characters_base-stats'):
    data_dir='.','stat_data','fe'+game
    data_dir=sep.join(data_dir)
    compiled_names=list()
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
                if '(' in name:
                    continue
                if name not in compiled_names:
                    compiled_names.append(name)
    return compiled_names


def translated_character_list(game,raw_list=None,file_match='characters_base-stats'):
    if raw_list is None:
        raw_list=character_list(game,file_match=file_match)
    new_list=list()
    for unit in raw_list:
        unit=updated_name_for(game,unit)
        new_list.append(unit)
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

def dict_generator(key_list,val_list):
    key_list=tuple(key_list)
    val_list=tuple(val_list)
    assert len(key_list) == len(val_list)
    my_dict=dict()
    for key,val in zip(key_list,val_list):
        my_dict[key]=val
    return my_dict

def unit_name_dict(game):
    val_list=character_list(game)
    key_list=translated_character_list(game)
    return dict_generator(key_list,val_list)

def fe4_name_dict(fe4family):
    assert fe4family in ('child','father')
    if fe4family == 'child':
        get_father=False
    else:
        get_father=True
    val_list=tuple(fe4_child_list(get_father=get_father))
    key_list=list()
    for val in val_list:
        new_name=updated_name_for('4',val)
        key_list.append(new_name)
    return dict_generator(key_list,val_list)

def get_true_name(game,unit,fe4family=None):
    if fe4family is not None:
        my_dict=fe4_name_dict(fe4family)
        message='Please specify a choice for the \'father\' option.'
    else:
        my_dict=unit_name_dict(game)
    if unit in my_dict.keys():
        return my_dict[unit]
    elif unit in my_dict.values():
        return unit
    else:
        game_title=game_title_dict(reverse=True)[game]
        message=(
            '',\
            '%s is not in FE%s: %s'%(unit,game,game_title),\
            'Please choose someone from the list above.',\
            ''
            )
        message='\n'.join(message)
        for key in my_dict.keys():
            print(key)
        print(message)
        raise Exception

def get_stat_names(game,stat_name=None):
    num_stats=read_stat_names(game)
    stats=list()
    for stat in num_stats.keys():
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        if x not in stats:
            stats.append(x)
    if stat_name is not None:
        return stats.index(stat_name)
    return stats

def read_class_names2(game,audit_name,match_name):
    name_file=r'fe'+game+'.csv'
    table='.','metadata','class_names',name_file
    table=sep.join(table)
    s=list()
    audit_match=[audit_name,match_name]
    with open(table) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            s.append(line)
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


if __name__ == '__main__':
    kw={'get_father':True}
    x=fe4_child_list(**kw)
    x=tuple(x)
    print(x)
