from os.path import sep
import pandas as pd

def get_display_name(d,name):
    if 'Father' in d.keys():
        suffix=d['Father']+'!'
    elif 'Lyn Mode' in d.keys():
        in_lyn_mode=d['Lyn Mode']
        suffix=('LM!' if in_lyn_mode else '')
    else:
        suffix=''
    return suffix+name

def gender_dict(game):
    path_to_genders=('.','metadata','genders.csv')
    gender_file=sep.join(path_to_genders)

    d={}

    with open(gender_file,'r') as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            if line[0] != game:
                if not d:
                    continue
                else:
                    break
            unit=line[1]
            gender=int(line[2])
            if gender == 0:
                x=' (M)'
            elif gender == 1:
                x=' (F)'
            elif gender == 2:
                x=' (Wagon)'
            else:
                suffix=' ('+unit+')'
                x=suffix
            d[unit]=x
    return d

def promo_dict(game,is_promo=False):
    promo_file=('.','metadata',r'genders.csv')
    promo_file=sep.join(promo_file)

    d={}

    with open(promo_file) as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            if line[0] != game:
                if not d:
                    continue
                else:
                    break
            unit=line[1]
            promo_path=line[3]
            if is_promo:
                if promo_path == 'NA':
                    x=True
                else:
                    x=False
                d[unit]=x
                continue
            if promo_path.isdigit():
                promo_path=int(promo_path)
                d[unit]=promo_path
    return d

def chapter_dict(game):
    data_loc='.','metadata',r'chapter_names.csv'
    data_loc=sep.join(data_loc)
    d={}
    with open(data_loc) as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            if line[0] != game:
                if d:
                    break
                else:
                    continue
            number=line[1]
            title=line[2]
            d[number]=title
    return d

def display_chapter_list(game,bonus_by_chapter):
    s=chapter_dict(game)
    column_names='Argument (as str)','Chapter Title','Levels'
    rows=list()
    for key,val in bonus_by_chapter.items():
        title=s[key]
        t=key,title,val
        rows.append(list(t))
    df=pd.DataFrame(rows)
    df.columns=column_names
    print(df)

def hard_mode_dict():
    elibe_hm='.','metadata',r'elibe_hm.csv'
    elibe_hm=sep.join(elibe_hm)
    level_dict={}
    with open(elibe_hm) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            unit=line[0]
            level=line[1]
            if not level.isdigit():
                continue
            level=int(level)
            chapter=line[2]
            if unit not in level_dict.keys():
                level_dict[unit]={}
            k=level_dict[unit]
            k[chapter]=level
    return level_dict


def auto_level_dict():
    auto_level='.','metadata',r'auto_level.csv'
    auto_level=sep.join(auto_level)
    level_dict={}
    with open(auto_level) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            unit=line[0]
            level=line[3]
            if not level.isdigit():
                continue
            level=int(level)
            early_chapter=line[1]
            late_chapter=line[2]
            if unit not in level_dict.keys():
                level_dict[unit]={}
            k=level_dict[unit]
            k[early_chapter]=0
            k[late_chapter]=level
    return level_dict


def auto_promo_dict():
    auto_promo='.','metadata',r'auto_promo.csv'
    auto_promo=sep.join(auto_promo)
    promo_dict={}
    with open(auto_promo) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            game=line[0]
            unit=line[1]
            if game in promo_dict.keys():
                promo_dict[game]+=(unit,)
            else:
                promo_dict[game]=(unit,)
    return promo_dict


def promo_level_dict(game,unit,unit_class='Dancer'):
    if unit in auto_promo_dict()[game]:
        x=1
    elif (game,unit,unit_class) == ('5','Lara','Dancer'):
        x=1
    elif game == '4':
        x=20
    else:
        x=10
    return x


def booster_dict(game):
    if game == '4':
        return {}
    else:
        bonus_dict={}
    booster_info='.','metadata',r'boosters.csv'
    booster_info=sep.join(booster_info)
    if game == '5':
        start_column=3
    elif game == '9':
        start_column=5
    else:
        start_column=1
    with open(booster_info) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            stat=line[0]
            bonus=line[start_column+1]
            if not bonus.isdigit():
                continue
            bonus=int(bonus)
            item=line[start_column]
            bonus_dict[item]=(stat,bonus)
    return bonus_dict


def names_dict(game,new_to_old=False):
    name_info='.','metadata',r'updated_names.csv'
    name_info=sep.join(name_info)
    names={}
    with open(name_info) as r_file:
        for line in r_file.readlines():
            line=line.strip()
            line=line.split(',')
            game_num,old_name,new_name=tuple(line)
            if game_num != game:
                if names:
                    break
                else:
                    continue
            if new_to_old:
                old_name,new_name=new_name,old_name
            names[old_name]=new_name
    return names


def updated_name_for(game,unit,new_to_old=False):
    names=names_dict(game,new_to_old=new_to_old)
    if unit in names.keys():
        unit=names[unit]
    return unit


def max_level_dict(game,class_name):
    scrubs='Journeyman','Recruit','Pupil'
    if game == '4':
        return 30
    elif class_name in scrubs:
        return 10
    else:
        return 20

def crusader_name(name):
    file='.','metadata',r'crusader-names.csv'
    file=sep.join(file)
    crusaders=dict()
    with open(file) as rfile:
        for line in rfile.readlines():
            line=line.strip()
            line=line.split(',')
            old=line[0]
            new=line[1]
            crusaders[old]=new
    if name in crusaders.keys():
        return crusaders[name]
    elif name in crusaders.values():
        return name

def scroll_equipper():
    file='.','metadata',r'fe5-scrolls.csv'
    file=sep.join(file)
    scroll_df=pd.read_csv(file,index_col=0)
    new_names=list()
    for col in scroll_df.index:
        new_name=crusader_name(col)
        new_names.append(new_name)
    scroll_df.index=new_names
    return scroll_df

if __name__=='__main__':
    x=scroll_equipper()
    print(x)
