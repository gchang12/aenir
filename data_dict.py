from os.path import sep, exists
from os import walk, mkdir
from aenir2.data_fetcher import save_stats
from aenir2.gender_dict import gender_dict
import pandas as pd

def read_stat_names(game):
    data_source=r'fe'+game+'.csv'
    file=('.','metadata','stat_names',data_source)
    file=sep.join(file)
    stat_names={}
    with open(file) as rFile:
        for line in rFile.readlines():
            line=line.strip()
            line=line.split(',')
            stat_names[line[0]]=line[1]
    return stat_names

def collect_table(table,headers,rows,files):
    with open(table,'r') as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            for stat in line:
                file=table.split(sep)[-1]
                if file not in headers:
                    headers.append(file)
                if stat not in rows.keys():
                    rows[stat]=['' for n in range(len(files))]
                column_num=files.index(file)
                stat_loc=line.index(stat)
                rows[stat][column_num]=str(stat_loc)
            break

def rows_and_headers_for(game):
    rows={}
    raw_data_path=('.','stat_data','fe'+game)
    raw_data_path=sep.join(raw_data_path)
    headers=[]
    for root,folders,files in walk(raw_data_path):
        if root != raw_data_path:
            continue
        for file in files:
            table=(raw_data_path,file)
            table=sep.join(table)
            collect_table(table,headers,rows,files)
    return rows,headers

def save_header_info(game):
    rows,headers=rows_and_headers_for(game)
    filename='table_headers.csv'
    path='.','audit','fe'+game,filename
    metadata_dir=sep.join(path[:-1])
    if not exists(metadata_dir):
        mkdir(metadata_dir)
    path=sep.join(path)
    with open(path,'w') as w_file:
        header_row=','+','.join(headers)
        w_file.write(header_row)
        for key,cells in rows.items():
            w_file.write('\n'+key+',')
            for cell in cells:
                y=(cell+',' if cell else ',')
                w_file.write(y)

def index_for_name(table,in_filename,stat_name):
    d={}
    headers={}
    with open(table,'r') as r_file:
        for line in r_file.readlines():
            line=line.strip().split(',')
            stat=line[0]
            if not stat:
                for col_num,name in enumerate(line):
                    if in_filename in name:
                        headers[col_num]=name
            else:
                if stat == stat_name:
                    for col_num,cell in enumerate(line):
                        if col_num not in headers.keys():
                            continue
                        if cell.isdigit():
                            d[headers[col_num]]=int(cell)
    return d

def name_for_index(table,index,find_in):
    headers={}
    names={}
    with open(table,'r') as Rfile:
        for line in Rfile.readlines():
            line=line.strip().split(',')
            stat=line[0]
            if not stat:
                for col_num,name in enumerate(line):
                    if find_in in name:
                        headers[col_num]=name
            else:
                for col_num,cell in enumerate(line):
                    if not cell.isdigit():
                        continue
                    if col_num not in headers.keys():
                        continue
                    if int(cell) == index:
                        names[headers[col_num]]=stat
    return names

def search_tables(game,x,in_filename):
    header_path='.','stat_data','fe'+game
    header_path=sep.join(header_path)
    if not exists(header_path):
        for k in range(4,10):
            save_header_info(str(k))
    search_results={}
    if type(x) == str:
        kwargs={'in_filename':in_filename,'stat_name':x}
        s=lambda table: index_for_name(table,**kwargs)
    elif type(x) == int:
        s=lambda table: name_for_index(table,x,in_filename)
    else:
        return {}
    for root,folders,files in walk(header_path):
        for file in files:
            table=(root,file)
            table=sep.join(table)
            search_results[file]=s(table)
    for result in search_results.values():
        for key,val in result.items():
            print(key,val)

def search_all_tables(x,in_filename):
    for k in range(4,10):
        game=str(k)
        args=(game,x,in_filename)
        search_tables(*args)
        print('\n')

def is_father(unit):
    file=('.','stat_data','fe4','characters_base-stats1.csv')
    file=sep.join(file)
    gen1_bases=pd.read_csv(file)
    parent_list=gen1_bases['Name'].values
    return unit in parent_list

def column_extractor(game,in_filename,index):
    assert type(index) in (str,int)
    data_folder=('.','stat_data','fe'+game)
    data_folder=sep.join(data_folder)
    names=list()
    for root,folders,files in walk(data_folder):
        for file in files:
            if in_filename not in file:
                continue
            data_file=(data_folder,file)
            data_file=sep.join(data_file)
            data=pd.read_csv(data_file)
            if type(index) == int:
                column=data.iloc[:,index]
            else:
                if index in data.columns:
                    column=data.loc[:,index]
            for val in column.values:
                #   Ignore numbers in FE4 bases-3
                if val.isdigit():
                    continue
                #   For HM blokes whose rowspan exceeds 1
                if 'HM' in val:
                    continue
                #   For FE4 kids whose fathers are listed with them
                #   'Character' column in *growths.csv columns but not searched
                if is_father(val) and column.name == 'Character':
                    continue
                #   For FE7 Wallace
                wallace_exception=(
                    val == 'General',\
                    column.name == 'Name',\
                    'classes' not in in_filename
                    )
                if all(wallace_exception):
                    continue
                names.append(val)
    return names

def character_bases(game):
    kwargs={
        'game':game,
        'in_filename':'base-stats',
        'index':'Class'}
    class_list=column_extractor(**kwargs)
    kwargs['index']=0
    character_list=column_extractor(**kwargs)
    char_to_class={}
    for cls,char in zip(class_list,character_list):
        char_to_class[char]=cls
    return char_to_class
    
def class_maxes(game):
    if game == '5':
        return ()
    kwargs={
        'game':game,
        'in_filename':'maximum-stats',
        'index':'Class'}
    class_list=column_extractor(**kwargs)
    return class_list

def class_promo(game):
    all_classes=list()
    if game == '7':
        file=('.','metadata','fe7_promo.csv')
        file=sep.join(file)
        columns=pd.read_csv(file,header=None)
        unpromoted=columns.iloc[:,0].values
        promoted=columns.iloc[:,1].values
        all_classes.extend(list(unpromoted))
        all_classes.extend(list(promoted))
        return all_classes
    kwargs={
        'game':game,
        'in_filename':'promotion-gains'}
    col_names='Class','Promotion'
    for name in col_names:
        kwargs['index']=name
        class_list=column_extractor(**kwargs)
        all_classes.extend(class_list)
    return all_classes

def class_growths(game):
    if game not in ('6','7','8'):
        return ()
    index=('Name' if game == '7' else 'Class')
    kwargs={
        'game':game,
        'in_filename':'classes_growth-rates',
        'index':index}
    class_list=column_extractor(**kwargs)
    return class_list

def read_class_names(game,audit_list,match_list):
    if game == '5':
        return {}
    d={}
    d[character_bases]='bases'
    d[class_growths]='growths'
    d[class_maxes]='maxes'
    d[class_promo]='promo'
    filename=r'fe'+game+'.csv'
    classes_table=('.','metadata','class_names',filename)
    classes_table=sep.join(classes_table)
    s=list()
    audit_match=[d[audit_list],d[match_list]]
    with open(classes_table) as r_file:
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

def write_difference(game,audit_list,match_to_list,difference):
    if not match_to_list(game) or not audit_list(game):
        return
    d={}
    d[character_bases]='character-bases'
    d[class_growths]='class-growths'
    d[class_maxes]='class-maxes'
    d[class_promo]='class-promo'
    part1=d[audit_list]
    part2=d[match_to_list]
    filename=(part1,part2)
    filename='classes_in_%s_not-in_%s.txt'%filename
    path=('.','audit','fe'+game,filename)
    audit_dir=sep.join(path[:-2])
    diff_dir=sep.join(path[:-1])
    if not exists(audit_dir):
        mkdir(audit_dir)
    if not exists(diff_dir):
        mkdir(diff_dir)
    path=sep.join(path)
    with open(path,'w') as wFile:
        for name in difference:
            wFile.write(name+'\n')


def bases_class_in_list(game,compare_list):
    #   For comparing character bases list to class attribute lists
    list_to_audit=character_bases(game)
    match_list=compare_list(game)
    gender=gender_dict(game)
    unmatched_items=set()
    name_matches=read_class_names(game,character_bases,compare_list)
    for char,class_name in list_to_audit.items():
        if char == 'L’Arachel':
            char='L\'Arachel'
        suffix=gender[char]
        gendered_class=class_name+suffix
        if class_name in match_list:
            continue
        if gendered_class in match_list:
            continue
        if class_name in name_matches.keys():
            proper_name=name_matches[class_name]
            if proper_name in match_list:
                continue
            gen_class=proper_name+suffix
            if gen_class in match_list:
                continue
        if gendered_class in name_matches.keys():
            proper_name=name_matches[class_name+suffix]
            if proper_name in match_list:
                continue
            if ' (' in proper_name:
                ungen_class=proper_name[:-4]
                if ungen_class in match_list:
                    return ungen_class
                else:
                    lord1=ungen_class+' (M)'
                    lord2=ungen_class+' (F)'
                    for name in (lord1,lord2):
                        if name in match_list:
                            return name
        else:
            unmatched_items|={class_name,gendered_class}
    write_difference(game,character_bases,compare_list,unmatched_items)
    return unmatched_items


def compare_class_lists(game,audit_list,match_to_list):
    #   For comparing class growths, promotion, and maxes lists
    list_to_audit=audit_list(game)
    list_to_match=match_to_list(game)
    unmatched=set()
    name_matches=read_class_names(game,audit_list,match_to_list)
    for cls in list_to_audit:
        if cls not in list_to_match:
            if cls in name_matches.keys():
                proper_name=name_matches[cls]
                if proper_name in list_to_match:
                    continue
                else:
                    unmatched|={cls}
    write_difference(game,audit_list,match_to_list,unmatched)
    return unmatched

def section_in_base_class_list(game,compare_list):
    base_class_dict=character_bases(game)
    genders=gender_dict(game)
    list_to_audit=compare_list(game)
    gendered_class_list=set()
    for character,cls in base_class_dict.items():
        gender=genders[character]
        gendered_class_list|={cls+gender}
    unmatched=set()
    for cls in list_to_audit:
        if cls in gendered_class_list:
            continue
        elif cls in base_class_dict.values():
            continue
        else:
            unmatched|={cls}
    write_difference(game,compare_list,character_bases,unmatched)
    return unmatched


def compile_all():
    class_attributes=class_maxes,class_promo,class_growths
    kwargs={}
    for k in range(4,10):
        game=str(k)
        kwargs['game']=game
        save_header_info(game)
        f=lambda attr1,attr2: compare_class_lists(game,attr1,attr2)
        for attribute in class_attributes:
            kwargs['compare_list']=attribute
            bases_class_in_list(**kwargs)
            section_in_base_class_list(**kwargs)
        for attribute in class_attributes:
            if attribute is class_attributes[-1]:
                break
            attr_loc=class_attributes.index(attribute)
            for sub_attr in class_attributes[attr_loc+1:]:
                f(attribute,sub_attr)
                f(sub_attr,attribute)


if __name__ == '__main__':
    compile_all()
