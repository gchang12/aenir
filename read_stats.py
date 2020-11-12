import os
import pandas as pd
from aenir2.data_dict import read_stat_names
from aenir2.gender_dict import gender_dict,promo_dict
from aenir2 import save_stats


def character_list(game,file_match='characters_base-stats'):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    compiled_names=()
    for root,folders,files in os.walk(data_dir):
        if root != data_dir:
            continue
        for file in files:
            if file_match not in file:
                continue
            filename=data_dir,file
            filename=os.path.sep.join(filename)
            table=pd.read_csv(filename,index_col=0)
            name_list=table.index
            for name in name_list:
                if name in compiled_names:
                    continue
                if 'HM' in name:
                    continue
                if name == 'General':
                    continue
                compiled_names+=(name,)
    return compiled_names


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
    count_list={}
    for unit in unit_list:
        if unit in count_list.keys():
            continue
        count_list[unit]=unit_list.count(unit)
    if get_father:
        yield 'Arden'
        condition = lambda unit: unit in parent_list
    else:
        condition = lambda unit: unit not in parent_list
    for unit,count in count_list.items():
        if condition(unit):
            yield unit


def load_child_attributes(unit,filename,father):
    #   Bases: characters_base-stats3.csv
    #   -   Exclude Celice, Leaf, Altenna
    #   Growths: characters_growth-rates4.csv
    kid_list=fe4_child_list()
    dad_list=fe4_child_list(get_father=True)
    #   Check if valid pair
    if unit not in kid_list:
        return
    elif father not in dad_list:
        return
    data_src='.','raw_data','fe4',filename
    data_src=os.path.sep.join(data_src)
    data=pd.read_csv(data_src)
    kwargs={
        'game':'4',
        'file_match':filename
        }
    #   Generate list to find index of father
    unit_list=character_list(**kwargs)
    unit_row_loc=unit_list.index(unit)
    father_column_loc=tuple(data.columns).index('Father')
    #   Will always be 'Arden'
    arden=data.iat[unit_row_loc,father_column_loc]
    #   Temporary row for unit with Arden as father
    unit_stats=data.iloc[unit_row_loc,:]
    if father == arden:
        return unit_stats
    #   Begin looking for father by searching through list
    get_pos=False
    for name in unit_list:
        if name == father:
            #   Does not get turned on until unit is found
            if not get_pos:
                continue
            father_row_loc=unit_list.index(name)
            break
        #   If found unit, then start searching for row with father
        if name == unit:
            get_pos=True
    #   Length of the rows subtracted by father index
    stop=len(data.columns)-father_column_loc
    #   Isolate row with father up until last numerical stat
    stats_slice=data.iloc[father_row_loc,:stop]
    corrected_stats=unit_stats[:father_column_loc],stats_slice
    #   Merge and rename row
    df=pd.concat(corrected_stats)
    df.index=data.columns
    return df


def load_child_stats(unit,filename,father):
    df=load_child_attributes(unit,filename,father)
    num_stats=read_stat_names('4')
    stat_names=list(num_stats.keys())
    data=df.loc[stat_names]
    return pd.Series(data,dtype='int64')


def load_child_bases(unit,father):
    filename='characters_base-stats3.csv'
    args=unit,filename,father
    return load_child_stats(*args)


def load_child_growths(unit,father):
    filename='characters_growth-rates4.csv'
    args=unit,filename,father
    return load_child_stats(*args)


def load_unit_info(game,unit,father='Arden',lyn_mode=False):
    data_dir='.','raw_data','fe'+game
    data_dir=os.path.sep.join(data_dir)
    unit_info={}

    unit_info['Game']=game
    unit_info['Name']=unit

    if unit in fe4_child_list():
        unit_info['Father']=father

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
        lyndis_league=character_list(
            game,\
            file_match='characters_base-stats1.csv'
            )
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


def zero_filler(game,file,row_data):
    if row_data is None:
        return
    row_data=row_data.to_dict()
    num_stats=read_stat_names(game)
    stats=()
    #   Consolidate names here
    for stat in num_stats.keys():
        if num_stats[stat]:
            x=num_stats[stat]
        else:
            x=stat
        stats+=(x,)
        #   Fill zeros here
        if x not in row_data.keys():
            row_data[x]=0
    for cell,stat in row_data.items():
        #   Resolve multi-promotion class errors
        if type(stat) == dict:
            for key,val in stat.items():
                row_data[cell]=val
    ordered_data={}
    #   Order stats here
    for stat in stats:
        ordered_data[stat]=row_data[stat]
    if file == 'classes_maximum-stats.csv':
        if game == '6':
            ordered_data['HP']=60
            ordered_data['Lck']=30
            ordered_data['Mov']=15
        if game == '9':
            ordered_data['Mov']=99
            ordered_data['Con']=99
            ordered_data['Wt']=99
    data=pd.Series(ordered_data)
    return data


def add_column(game,filename,data):
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
    add_column(game,filename,data)
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

    gendered_class=class_name+suffix

    #   Check if name without suffix appears in page
    if class_name in match_list:
        return class_name

    #   Check if gendered version of that name appears
    if gendered_class in match_list:
        return gendered_class

    #   Check if name with gender-suffix appears
    if class_name in name_matches.keys():
        proper_name=name_matches[class_name]
        if proper_name in match_list:
            return proper_name
        gendered_class2=proper_name+suffix
        if gendered_class2 in match_list:
            return gendered_class2

    #   Check if corrected version of name appears
    if gendered_class in name_matches.keys():
        proper_name=name_matches[gendered_class]
        if proper_name in match_list:
            return proper_name
        if ' (' in proper_name:
            ungen_class=proper_name[:-4]
            if ungen_class in match_list:
                return ungen_class


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
                row_data=data.loc[name,:]
                if file != 'classes_promotion-gains.csv':
                    x=zero_filler(game,file,row_data)
                else:
                    x=row_data
                return x
            else:
                continue


def load_character_bases(game,unit_name,lyn_mode=False,father='Arden'):
    file_match='characters_base-stats'
    exceptions=()
    if game == '4':
        #   For FE4 kids
        if unit_name in fe4_child_list():
            data=load_child_bases(unit_name,father)
            return data
        #   Back to main routine
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


def load_character_growths(game,unit_name,father='Arden'):
    file_match='characters_growth-rates'
    exceptions=()
    if game == '4':
        #   For FE4 kids
        if unit_name in fe4_child_list():
            data=load_child_growths(unit_name,father)
            return data
        #   Return to main routine if fails
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


def get_class_name(game,unit,class_name,lyn_mode):
    if not class_name:
        unit_info=load_unit_info(game,unit,lyn_mode=lyn_mode)
        class_name=unit_info['Class']
    proper_name=lambda file: match_class_name(game,unit,class_name,file)
    return proper_name


def load_class_maxes(game,unit,class_name='',lyn_mode=False):
    if game == '5':
        maxes_data='.','metadata','fe5_maxes.csv'
        maxes_data=os.path.sep.join(maxes_data)
        data=pd.read_csv(maxes_data,index_col=0,header=None,squeeze=True)
        return data
    file_match='classes_maximum-stats'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


def load_class_promo(game,unit,class_name='',promo_path=0,lyn_mode=False):
    file_match='classes_promotion-gains.csv'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
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
    data=zero_filler(game,file_match,data)
    return data


def load_class_promo_dict(game,promo_path=0):
    filename='classes_promotion-gains.csv'
    file='.','raw_data','fe'+game,filename
    file=os.path.sep.join(file)
    data=pd.read_csv(file,index_col=0)
    #   Exception for FE7 promo-table; does not have unpromoted classes column
    if game == '7':
        promoted=tuple(data.index)
    else:
        promoted=tuple(data.iloc[:,0])
    #   Add unpromoted classes and set as index
    add_column(game,filename,data)
    unpromoted=tuple(data.index)
    d={}
    count=0
    exclude_list=()
    for scrub,elite in zip(unpromoted,promoted):
        if scrub in exclude_list:
            continue
        if scrub in d.keys():
            count+=1
            if count == promo_path:
                d[scrub]=elite
                exclude_list+=(scrub,)
                count=0
        else:
            d[scrub]=elite
    return d


def load_class_growths(game,unit,class_name='',lyn_mode=False):
    if game not in ('6','7'):
        return
    file_match='classes_growth-rates'
    proper_name=get_class_name(game,unit,class_name,lyn_mode)
    kwargs={
        'game':game,\
        'name':proper_name,\
        'file_match':file_match,
        }
    data=load_stats(**kwargs)
    return data


def test_stat_retrieval(game,unit=''):
    lord={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    if not unit:
        unit=lord[game]
    args=game,unit
    test_cases=load_character_bases,\
                load_character_growths,\
                load_class_maxes,\
                load_class_promo,\
                load_class_growths
    all_data=()
    unit_info=load_unit_info(*args)
    indices=()
    for case in test_cases:
        data=case(*args)
        if data is None:
            continue
        all_data+=(data,)
        index_copy=tuple(data.index)
        if index_copy not in indices:
            indices+=(index_copy,)
    df=pd.DataFrame(all_data)
    for item in unit_info.items():
        print(item)
    print(df)
    same_indices=len(indices) == 1
    message='All columns have identical indices: %s'%same_indices
    print(message)


def test_class_promo_dict(game='8',promo_path=1):
    x=load_class_promo_dict(game,promo_path=promo_path)
    for stuff in x.items():
        print(stuff)


def test_unit_list(game='7',lyn_mode=False):
    file_match='characters_base-stats'
    if lyn_mode:
        y='1'
    else:
        y='2'
    file_match+=y
    x=character_list(game,file_match=file_match)
    for unit in x:
        print(unit)

def test_child_list():
    x=fe4_child_list()
    for m in x:
        print(m)


def test_child_hunt(unit='Rana',father='Claude'):
    args='4',unit
    test_cases=load_character_bases,\
                load_character_growths,\
                load_class_maxes,\
                load_class_promo,\
                load_class_growths
    all_data=()
    unit_info=load_unit_info(*args,father=father)
    indices=()
    for case in test_cases:
        try:
            data=case(*args,father=father)
        except:
            data=case(*args)
        if data is None:
            continue
        all_data+=(data,)
        index_copy=tuple(data.index)
        if index_copy not in indices:
            indices+=(index_copy,)
    df=pd.DataFrame(all_data)
    for item in unit_info.items():
        print(item)
    print(df)
    same_indices=len(indices) == 1
    message='All columns have identical indices: %s'%same_indices
    print(message)


def test_match_name(unit='Ross',class_name='Journeyman (2)',match_against_maxes=True):
    game='8'
    if match_against_maxes:
        filename='classes_maximum-stats.csv'
    else:
        filename='classes_promotion-gains.csv'
    x=match_class_name(game,unit,'Journeyman (2)',filename,audit='promo')
    print(x)


if __name__=='__main__':
    k=8
    game=str(k)
    lord={
        '4':'Sigurd',
        '5':'Leaf',
        '6':'Roy',
        '7':'Eliwood',
        '8':'Eirika',
        '9':'Ike'
        }
    test_child_hunt()
