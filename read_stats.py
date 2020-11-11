import os
import pandas as pd
from aenir2.data_dict import read_stat_names
from aenir2.gender_dict import gender_dict,promo_dict
from aenir2 import save_stats


def get_row_headers(game,filename):
    table=pd.read_csv(filename,index_col=0)
    return table.index


def character_list(game,lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    compiled_names=()
    file_match='characters_base-stats'
    if lyn_mode:
        file_match+='1'
    for root,folders,files in os.walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_match not in file:
                continue
            filename=data_dir,file
            filename=os.path.sep.join(filename)
            name_list=get_row_headers(game,filename)
            for name in name_list:
                if name in compiled_names:
                    continue
                compiled_names+=(name,)
    x=compiled_names
    if lyn_mode:
        x=compiled_names[:-1]
    return x


def load_unit_info(game,unit,lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    unit_info={}
    
    unit_info['Game']=game
    unit_info['Name']=unit

    if unit == 'Wallace':
        promo_status=not lyn_mode
    else:
        is_promo=promo_dict(game,is_promo=True)
        promo_status=is_promo[unit]
    unit_info['Promoted']=promo_status
    
    file_substr='characters_base-stats'

    if game == '7':
        if lyn_mode:
            suffix='1'
        else:
            suffix='2'
        lyndis_league=character_list(game,lyn_mode=True)
        if unit in lyndis_league:
            unit_info['Lyn Mode']=lyn_mode
        file_substr+=suffix
    for root,folders,files in os.walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_substr not in file:
                continue
            data_file=data_dir,file
            data_file=os.path.sep.join(data_file)
            data=pd.read_csv(data_file,index_col=0)
            if 'Lv' in data.columns:
                col='Lv'
            elif 'Level' in data.columns:
                col='Level'
            if unit in data.index:
                unit_info['Class']=data.at[unit,'Class']
                unit_info['Level']=data.at[unit,col]
    return unit_info


def zero_filler(row_data):
    num_stats=read_stat_names(game)
    for stat in num_stats.keys():
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        if x not in row_data.keys():
            row_data[x]=0
    for cell,stat in row_data.items():
        if type(stat) == dict:
            for key,val in stat.items():
                row_data[cell]=val
    data=pd.Series(row_data)
    return data


def read_stat_table(game,filename):
    file='.','raw_data','fe'+game,filename
    file=os.path.sep.join(file)
    df=pd.read_csv(file,index_col=0)
    num_stats=read_stat_names(game)
    stat_names=()
    for stat in num_stats.keys():
        if stat not in df.columns:
            continue
        stat_names+=(stat,)
    data=df.loc[:,stat_names]
    new_stat_names=()
    for stat in stat_names:
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        new_stat_names+=(x,)
    data.columns=new_stat_names
    if (game,filename) == ('7','classes_promotion-gains.csv'):
        #   SF page for FE7 does not have column for unpromoted classes
        promo_file='.','metadata',r'fe7_promo.csv'
        promo_file=os.path.sep.join(promo_file)
        unpromoted=()
        with open(promo_file) as r_file:
            index=0
            for line in r_file.readlines():
                line=line.strip()
                line=line.split(',')
                unpromoted+=(line[0],)
                #   Just to match correct classes to each other
                assert line[1] == data.index[index]
                index+=1
        promoted=tuple(data.index)
        data.index=unpromoted
        data.rename_axis(axis=0,mapper='Class',inplace=True)
    return data


def read_class_names2(game,audit_name,match_name):
    name_file=r'fe'+game+'.csv'
    table='.','metadata','class_names',name_file
    table=os.path.sep.join(table)
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


def match_class_name(game,unit,class_name,filename,audit='bases'):
    assert 'classes' in filename
    categories={
        'base-stats':'bases',\
        'growth-rates':'growths',\
        'maximum-stats':'maxes',\
        'promotion-gains':'promo'
        }

    for substring,codename in categories.items():
        if substring in filename:
            code=categories[substring]
            break

    gender_for=gender_dict(game)
    suffix=gender_for[unit]
    x=read_stat_table(game,filename)
    match_list=x.index
    name_matches=read_class_names2(game,audit,code)

    #   Check if name without suffix appears in page
    if class_name in match_list:
        return class_name

    #   Check if name with gender-suffix appears
    elif class_name in name_matches.keys():
        proper_name=name_matches[class_name]
        if proper_name in match_list:
            return proper_name

    gendered_class=class_name+suffix

    #   Check if corrected version of name appears
    if gendered_class in name_matches.keys():
        proper_name=name_matches[gendered_class]
        if proper_name in match_list:
            return proper_name

    #   Check if gendered version of that name appears
    elif gendered_class in match_list:
        return gendered_class


def load_stats(game,name,file_match,exceptions=()):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)

    if not os.path.exists(data_dir):
        save_stats(game)
    for root,folders,files in os.walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_match not in file:
                continue
            if file in exceptions:
                continue
            data=read_stat_table(game,file)
            if callable(name):
                name=name(file)
            if name in data.index:
                row_data=data.loc[name,:].to_dict()
                zf_data=zero_filler(row_data)
                return zf_data
            else:
                continue


def load_character_bases(game,unit_name,lyn_mode=False):
    file_match='characters_base-stats'
    exceptions=()
    if game == '4':
        baldr_family='Celice','Leaf','Altenna'
        if unit_name not in baldr_family:
            exceptions+=('characters_base-stats3.csv',)
    elif game == '7':
        table_num=('1.csv' if not lyn_mode else '2.csv')
        exceptions+=('characters_base-stats'+table_num,)
    kwargs={
        'game':game,\
        'name':unit_name,\
        'file_match':file_match,\
        'exceptions':exceptions
        }
    data=load_stats(**kwargs)
    return data


def load_character_growths(game,unit_name):
    file_match='characters_growth-rates'
    exceptions=()
    if game == '4':
        exceptions+=(
            'characters_growth-rates1.csv',\
            'characters_growth-rates4.csv'
            )
    kwargs={
        'game':game,\
        'name':unit_name,\
        'file_match':file_match,\
        'exceptions':exceptions
        }
    data=load_stats(**kwargs)
    return data


def load_class_maxes(game,unit,class_name='',lyn_mode=False):
    if game == '5':
        maxes_data='.','metadata','fe5_maxes.csv'
        maxes_data=os.path.sep.join(maxes_data)
        data=pd.read_csv(maxes_data,index_col=0,header=None,squeeze=True)
        return data
    file_match='classes_maximum-stats'
    exceptions=()
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
    proper_name=lambda file: match_class_name(game,unit,class_name,file)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


def load_class_promo(game,unit,class_name='',promo_path=0,lyn_mode=False):
    file_match='classes_promotion-gains'
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
    proper_name=lambda file: match_class_name(game,unit,class_name,file)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    if type(data) == pd.DataFrame:
        t=promo_dict(game)
        if unit in t.keys():
            promo_path=t[unit]
        assert 0 <= promo_path < len(data)
        data=data.iloc[promo_path,:]
    return data


def load_class_growths(game,unit,class_name='',lyn_mode=False):
    if game not in ('6','7'):
        return
    file_match='classes_growth-rates'
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
    proper_name=lambda file: match_class_name(game,unit,class_name,file)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


if __name__=='__main__':
    k=7
    game=str(k)
    lord={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    #unit='Geitz'
    unit=lord[game]
    args=game,unit
    test_cases=load_character_bases,\
                load_character_growths,\
                load_class_maxes,\
                load_class_promo,\
                load_class_growths
    all_data=()
    unit_info=load_unit_info(*args)
    for case in test_cases:
        data=case(*args)
        if data is None:
            continue
        all_data+=(data,)
    df=pd.DataFrame(all_data)
    for item in unit_info.items():
        print(item)
    print(df)
