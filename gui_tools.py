from tkinter import font,LabelFrame,StringVar,Listbox,N,S,W,E,Scrollbar

from aenir2.name_lists import character_list,\
     translated_character_list,\
     get_stat_names,\
     fe4_child_list,\
     game_title_dict
from aenir2.gender_dict import max_level_dict,\
     updated_name_for,\
     hard_mode_dict,\
     auto_level_dict,\
     booster_dict,\
     chapter_dict

def underline_font(myLabel):
    my_font=font.Font(myLabel,myLabel.cget('font'))
    my_font.configure(underline=True)
    myLabel.configure(font=my_font)

def set_mainframe(row,column,width,height,rowspan=1,text=' '):
    kw={
        'padx':4,\
        'pady':4,\
        'borderwidth':2,\
        'width':width,\
        'height':height,\
        'relief':'sunken',\
        'text':text
        }
    frame=LabelFrame(**kw)
    frame.grid_propagate(0)
    grid_kw={
        'padx':10,\
        'pady':0
        }
    frame.grid(row=row,column=column,rowspan=rowspan,**grid_kw)
    return frame

def select_from_list(master,itemlist,height,add_scrollbar=False):
    list_var=StringVar(value=itemlist)

    kwargs={
        'master':master,\
        'listvariable':list_var,\
        'height':height,\
        'width':30
        }
    item_list=Listbox(**kwargs)
    item_list.grid(column=0,sticky=N+W+S,row=0)

    if add_scrollbar:
        scrollbar=Scrollbar(master)
        scrollbar.grid(column=1,sticky=N+S,rowspan=2,row=0)
        scrollbar.config(command=item_list.yview)
        item_list['yscrollcommand']=scrollbar.set

    return item_list

def anakin(frame):
    assert type(frame) == LabelFrame
    temple=frame.winfo_children()
    for youngling in temple:
        youngling.destroy()

def listbox_jump(listbox,*args):
    x=args[0].keysym
    current_index=listbox.curselection()[0]
    height=listbox['height']
    length=listbox.size()-1
    listbox.selection_clear(0,length)
    if x in ('End','Home'):
        if x == 'End':
            target=length
        else:
            target=0
        number=target-current_index
        listbox.yview_scroll(number,'units')
    elif x in ('Prior','Next'):
        number=2
        if x == 'Prior':
            target=current_index - height
            if target < 0:
                target=0
            number=-number
        else:
            target=current_index+height
            if target > length:
                target=length
        listbox.yview_scroll(number,'units')
    else:
        return
    listbox.activate(target)
    listbox.select_set(target)
    listbox.select_anchor(target)
    

def bind_listbox_shortcuts(listbox):
    keys='<End>','<Home>','<Prior>','<Next>'
    bind_to_shortcuts=lambda *args: listbox_jump(listbox,*args)
    for key in keys:
        listbox.bind(key,bind_to_shortcuts)

#   Conditions that Limstella class needs to check before initialization

def max_level(game,class_name):
    args=(game,class_name)
    max_level=max_level_dict(*args)
    return max_level

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

def decline_hugh_dict():
    d={
        '10,000':0,\
        '8,000':1,\
        '6,000':2,\
        '5,000':3
        }
    return d

if __name__ == '__main__':
    x=fe4_father_list()
    print(len(x))
