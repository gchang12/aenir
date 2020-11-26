from aenir2.read_stats import *
from aenir2.gender_dict import *
from aenir2.name_lists import stat_names,character_list,fe4_child_list
from numpy import array,zeros
from copy import deepcopy

class Morph:
    def __init__(self,game,unit,lyn_mode=False,father='Arden'):
        assert unit in character_list(game)
        assert father in fe4_child_list(get_father=True)
        kwargs={
            'game':game,\
            'unit':unit,\
            'father':father,\
            'lyn_mode':lyn_mode
            }
        self.kwargs=kwargs.copy()
        self.unit_info=load_unit_info(**kwargs)
        self.game=self.unit_info.pop('Game')
        self.unit=self.unit_info.pop('Name')
        self.base_class=self.unit_info.pop('Class')
        self.base_level=self.unit_info.pop('Level')
        self.base_stats=load_character_bases(**kwargs).to_numpy()
        self.growth_rates=load_character_growths(**kwargs).to_numpy()
        #   Start update for class attribute loaders here
        d={}
        d['audit']='bases'
        d['class_name']=self.base_class
        kwargs.update(d)
        self.maximum_stats=load_class_maxes(**kwargs).to_numpy()
        self.promotions=load_class_promo_list(**kwargs)
        #   Start mutable attributes here
        if self.promotions is not None:
            self.my_levels=[self.base_level,None]
            self.my_promotions=self.promotions.copy()
            self.my_classes=[self.base_class,None]
        else:
            self.my_levels=[None,self.base_level]
            self.my_promotions=None
            self.my_classes=[None,self.base_class]
        self.my_maxes=self.maximum_stats.copy()
        self.my_stats=self.base_stats.copy()

    def min_promo_level(self,promo_path=0):
        promo_class=self.my_promotions[promo_path]
        kwargs0={
            'game':self.game,\
            'unit':self.unit,\
            'unit_class':promo_class
            }
        min_promo_lv=promo_level_dict(**kwargs0)
        return min_promo_lv
    
    def can_promote(self):
        trainees='Ross','Amelia','Ewan'
        lara_promotions=['Thief','Thief Fighter','Dancer','Thief Fighter'],\
                         ['Thief','Dancer','Thief Fighter']
        if self.my_promotions is None:
            x=False
        elif self.unit in trainees:
            if len(self.my_classes) > 2:
                x=False
            else:
                x=True
        elif self.unit == 'Lara':
            if self.my_classes in lara_promotions:
                x=False
            else:
                x=True
        else:
            x=True
        return x

    #   Methods to help identify correct attribute to update

    def current_index(self):
        if self.can_promote():
            if self.my_classes[-1] is not None:
                index=-1
            else:
                index=0
        else:
            index=-1
        return index
    
    def current_level(self,get_level=True):
        if get_level:
            x=self.my_levels
        else:
            x=x=self.my_classes
        index=self.current_index()
        return x[index]

    def current_class(self):
        return self.current_level(get_level=False)

    #   Modify Morph attributes here

    def cap_stats(self):
        capped_array=()
        for stat,limit in zip(self.my_stats,self.my_maxes):
            if stat > limit:
                stat=limit
            capped_array+=(stat,)
        self.my_stats=array(capped_array)

    def level_up(self,num_levels,stat_array=None,increase_level=True,increase_stats=True):
        #   Check if valid action - IMPORT TO TKINTER
        max_level=max_level_dict(self.game,self.current_class())
        if self.current_level() >= max_level:
            return
        if self.current_level() + num_levels > max_level:
            num_levels=max_level-self.current_level()
        if stat_array is None:
            stat_array=self.growth_rates
        if increase_level:
            index=self.current_index()
            self.my_levels[index]+=num_levels
        if increase_stats:
            self.my_stats=self.my_stats+stat_array*num_levels/100
        self.cap_stats()

    def promote(self,promo_path=0):
        #   Check if valid action - IMPORT TO TKINTER
        if not self.can_promote():
            return
        #   Correcting promotion path here - IMPORT TO TKINTER
        promo_indices=tuple(self.my_promotions.keys())
        if len(promo_indices) == 1:
            promo_path=promo_indices[0]
        promo_class=self.my_promotions[promo_path]
        audit=('bases' if self.my_classes[-1] is None else 'promo')
        kwargs1={
            'class_name':self.current_class(),\
            'promo_path':promo_path,\
            'audit':audit
            }
        kwargs1.update(self.kwargs)
        promo_bonus=load_class_promo(**kwargs1).to_numpy()
        #   Checks if unit can promote at current level
        #   -if no, automatically levels up unit
        #   -IMPORT TO TKINTER
        min_promo_lv=self.min_promo_level(promo_path=promo_path)
        if self.current_level() < min_promo_lv:
            num_levels=min_promo_lv-self.current_level()
            self.level_up(num_levels)
        self.my_stats=self.my_stats+promo_bonus

        def append_upgrade(list_var,value):
            if list_var[-1] is None:
                list_var[-1]=value
            else:
                list_var+=[value]

        if self.game == '4':
            reset_level=self.current_level()
        else:
            reset_level=1

        append_upgrade(self.my_levels,reset_level)
        append_upgrade(self.my_classes,promo_class)

        kwargs2={
            'class_name':promo_class,\
            'audit':'promo'
            }
        kwargs2.update(self.kwargs)
        self.my_maxes=load_class_maxes(**kwargs2).to_numpy()
        self.cap_stats()
        self.my_promotions=load_class_promo_list(**kwargs2)
        if not self.can_promote():
            self.my_promotions=None

    def class_level_up(self,num_levels,increase_stats,increase_level):
        #   Check if valid action - IMPORT TO TKINTER
        if None not in self.my_classes:
            return
        kwargs={
            'class_name':self.base_class,\
            'audit':'bases'
            }
        kwargs.update(self.kwargs)
        class_growths=load_class_growths(**kwargs)
        if class_growths is None:
            return
        kwargs={
            'num_levels':num_levels,\
            'stat_array':class_growths.to_numpy(),\
            'increase_stats':increase_stats,\
            'increase_level':increase_level
            }
        return self.level_up(**kwargs)

    def add_hm_bonus(self,num_levels=None,chapter=''):
        if num_levels is None:
            #   Check if valid action - IMPORT TO TKINTER
            if self.unit in hard_mode_dict().keys():
                bonus_by_chapter=hard_mode_dict()[self.unit]
                num_levels=bonus_by_chapter[chapter]
            else:
                return
        kwargs={
            'num_levels':num_levels,\
            'increase_stats':True,\
            'increase_level':False
            }
        return self.class_level_up(**kwargs)

    def add_auto_bonus(self,chapter=''):
        #   Check if valid action - IMPORT TO TKINTER
        if self.unit in auto_level_dict().keys():
            bonus_by_chapter=auto_level_dict()[self.unit]
            num_levels=bonus_by_chapter[chapter]
        elif self.unit in ('Ephraim','Eirika'):
            num_levels=15-self.current_level()
        else:
            return
        if self.unit == 'Gonzales':
            increase_stats=False
        else:
            increase_stats=True
        kwargs={
            'num_levels':num_levels,\
            'increase_stats':increase_stats,\
            'increase_level':True
            }
        return self.class_level_up(**kwargs)

    def use_stat_booster(self,stat_name):
        bonus_dict=booster_dict(self.game,get_bonus=True)
        bonus=bonus_dict[stat_name]
        stat_loc=stat_names(self.game,stat_name=stat_name)
        boost_array=zeros(len(self.my_stats))
        boost_array[stat_loc:stat_loc+1].fill(bonus)
        self.my_stats=self.my_stats+boost_array
        self.cap_stats()

    def decline_hugh(self,num_times):
        #   Check if valid action - IMPORT TO TKINTER
        if num_times not in range(4):
            return
        elif self.unit != 'Hugh':
            return
        decrement=zeros(len(self.my_stats))
        decrement[:-2].fill(-num_times)
        self.my_stats=self.my_stats+decrement

    #   For Aenir class

    def copy(self):
        #   For determining forecast
        return deepcopy(self)

    def __gt__(self,other):
        #   Indicates which stats to color during forecast
        #   True: blue
        #   False: red
        #   None: (no color)
        colors={}
        stat_array=zip(stat_names(self.game),self.my_stats,other.my_stats)
        for name,my_stat,other_stat in stat_array:
            if my_stat == other_stat:
                x=None
            elif my_stat > other_stat:
                x=True
            elif my_stat < other_stat:
                x=False
            colors[name]=x
        def update_colors(key,f1,f2):
            if f1() == f2():
                x=None
            else:
                x=True
            colors[key]=x
        update_colors('Class',self.current_class,other.current_class)
        update_colors('Level',self.current_level,other.current_level)
        return colors


if __name__=='__main__':
    k=8
    game=str(k)
    unit='Ross'
    args=(game,unit)
    x=Morph(*args)
    x.level_up(9)
    y=x.copy()
    y.promote()
    print(x < y)
