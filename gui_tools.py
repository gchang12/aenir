from tkinter import font

from aenir2.name_lists import character_list,\
     translated_character_list,\
     stat_names,\
     fe4_child_list,\
     game_title_dict
from aenir2.gender_dict import max_level_dict,\
     updated_name_for,\
     hard_mode_dict,\
     auto_level_dict,\
     booster_dict,\
     chapter_dict

def max_level(game,class_name):
    args=(game,class_name)
    max_level=max_level_dict(*args)
    return max_level

#   Conditions that Limstella class needs to check before initialization

def is_lyndis_league(game,unit):
    #   Essential to summoning Lyn Mode dialog box
    if game != '7':
        return False
    kwargs={
        'game':game,\
        'file_match':'characters_base-stats1.csv'
        }
    unit_list=character_list
    lyndis_league=unit_list(**kwargs)
    return unit in lyndis_league

def is_fe4_child(game,unit):
    #   Essential to summoning father selection window
    if game != '4':
        return False
    else:
        return unit in fe4_child_list()

#   Getting lists

def fe4_father_list():
    father_list=fe4_child_list(get_father=True)
    kwargs={
        'game':'4',\
        'raw_list':father_list
        }
    return translated_character_list(**kwargs)

def unit_list(game):
    return translated_character_list(game)

#   For displayed unit names

def get_old_name(game,unit):
    return updated_name_for(game,unit,new_to_old=True)

#   After initialization of Morph object

def is_hugh(game,unit):
    #   Use self.decline_hugh method
    return (game,unit) == ('6','Hugh')

def has_hm_bonus(game,unit):
    return unit in hard_mode_dict().keys()

def has_auto_bonus(game,unit):
    return unit in auto_level_dict().keys()

def get_hm_chapters(unit):
    d=hard_mode_dict()[unit]
    if '' not in d.keys():
        return tuple(d.keys())

def get_auto_chapters(unit):
    d=auto_level_dict()[unit]
    return tuple(d.keys())

def booster_to_stat_converter(game,booster_name):
    d=booster_dict(game,get_bonus=False)
    t={}
    for stat_name,item in d.items():
        t[item]=stat_name
    return t

#   Checks if certain actions permissible (e.g. level-up, promote)

def can_auto_level_fe8_lord(game,unit,current_level):
    if game != '8':
        return False
    elif unit not in ('Ephraim','Eirika'):
        return False
    return current_level >= 15

def underline_font(myLabel):
    my_font=font.Font(myLabel,myLabel.cget('font'))
    my_font.configure(underline=True)
    myLabel.configure(font=my_font)

if __name__ == '__main__':
    x=fe4_father_list()
    print(len(x))
