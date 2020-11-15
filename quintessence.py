from aenir2.read_stats import *
from aenir2.gender_dict import *
from numpy import array,zeros

class Morph:
    def __init__(self,game,unit,lyn_mode=False,father='Arden'):
        kwargs={
            'game':game,\
            'unit':unit,\
            'father':father,\
            'lyn_mode':lyn_mode
            }
        self.kwargs=kwargs
        self.unit_info=load_unit_info(**kwargs)
        #   Game: game
        #   Name: unit_name
        #   Promoted: is_promoted
        #   Class: unit_class
        #   Level: base_level

        #   *Not available for some units*
        #   Father: father
        #   Lyn Mode: lyn_mode
        self.game=self.unit_info['Game']
        self.unit=self.unit_info['Name']
        self.unit_class=self.unit_info['Class']
        self.base_level=self.unit_info['Level']
        self.base_stats=load_character_bases(**kwargs).to_numpy()
        self.growth_rates=load_character_growths(**kwargs).to_numpy()/100
        self.maximum_stats=load_class_maxes(**kwargs).to_numpy()
        self.promotions=load_class_promo_list(**kwargs)
        #   Start mutable attributes here
        if self.promotions is not None:
            self.my_levels=[self.base_level,None]
            self.my_promotions=self.promotions.copy()
            self.my_classes=[self.unit_class,None]
        else:
            self.my_levels=[None,self.base_level]
            self.my_promotions=None
            self.my_classes=[None,self.unit_class]
        self.my_maxes=self.maximum_stats.copy()
        self.my_stats=self.base_stats.copy()

    def current_level(self,current_class=False):
        if self.my_promotions is None:
            index=-1
        else:
            index=0
        if current_class:
            x=self.my_classes
        else:
            x=self.my_levels
        return x[index]

    def cap_stats(self):
        capped_array=()
        for stat in zip(self.my_stats,self.my_maxes):
            if stat > limit:
                stat=limit
            capped_array+=(stat,)
        self.my_stats=array(capped_array)

    def level_up(self,num_levels,stat_array=None,increase_level=True,increase_stats=True):
        max_level=max_level_dict(self.game,self.my_class)
        if current_level() >= max_level:
            return
        if current_level() + num_levels > max_level:
            num_levels=max_level-current_level()
        if stat_array is None:
            stat_array=self.growth_rates
        if increase_level:
            index=(0 if self.my_promotions is not None else -1)
            self.my_levels[index]+=num_levels
        if increase_stats:
            self.my_stats=self.my_stats+stat_array*num_levels
        self.cap_stats()

    def promote(self,promo_path=0):
        promo_indices=tuple(self.my_promotions.keys())
        if self.my_promotions is None:
            return
        #   Checks:
        #   If unit is in list of units that do not have minimum level for promotion
        #   If unit level is at least minimum level for promotion
        elif not promo_level_dict(self.game,self.unit,current_level()):
            return
        #   For people who want to promote Lara three times:
        #   1 Thief
        #   2 Thief Fighter
        #   3 Dancer
        #   4 Thief Fighter
        elif len(self.my_classes) > 3:
            return
        elif len(promo_indices) == 1:
            promo_path=promo_indices[0]
        kwargs1={
            'class_name':self.current_level(current_class=True),\
            'promo_path':promo_path
            }
        kwargs1.update(self.kwargs)
        promo_bonus=load_class_promo(**kwargs1).to_numpy()
        self.my_stats=self.my_stats+promo_bonus
        if self.game == '4':
            reset_level=self.current_level()
        else:
            reset_level=1

        def append_upgrade(list_var,value):
            if list_var[-1] is None:
                list_var[-1]=value
            else:
                list_var+=[value]

        append_upgrade(self.my_levels,reset_level)
        append_upgrade(self.my_classes,self.my_promotions[promo_path])

        kwargs2={
            'class_name':self.current_level(current_class=True)
            }
        kwargs2.update(self.kwargs)
        self.my_maxes=load_class_maxes(**kwargs2).to_numpy()
        self.cap_stats()
        self.my_promotions=load_class_promo_list(**kwargs2)

    def class_level_up(self,num_levels,increase_stats,increase_level):
        class_growths=load_class_growths(**self.kwargs)
        if class_growths is None:
            return
        kwargs={
            'num_levels':num_levels,\
            'stat_array':class_growths.to_numpy(),\
            'increase_stats':increase_stats,\
            'increase_level':increase_level
            }
        self.level_up(**kwargs)

    def add_hm_bonus(self,num_levels=None,chapter=''):
        if num_levels is None:
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
        self.class_level_up(**kwargs)

    def add_auto_bonus(self,chapter):
        if self.unit not in auto_level_dict().keys():
            return
        if self.unit == 'Gonzales':
            increase_stats=False
        else:
            increase_stats=True
        bonus_by_chapter=auto_level_dict()[self.unit]
        num_levels=bonus_by_chapter[chapter]
        kwargs={
            'num_levels':num_levels,\
            'increase_stats':increase_stats,\
            'increase_level':True
            }
        self.class_level_up(**kwargs)

    def use_stat_booster(self,stat_name):
        bonus_dict=booster_dict(self.game,get_bonus=True)
        bonus=bonus_dict[stat_name]
        stat_loc=stat_names(self.game,stat_name=stat_name)
        boost_array=zeros(len(self.my_stats))
        boost_array[stat_loc:stat_loc+1].fill(bonus)
        self.my_stats=self.my_stats+boost_array
        self.cap_stats()

    def is_capped(self):
        return self.my_stats == self.my_maxes

    def decline_hugh(self,num_times):
        if num_times not in range(4):
            return
        elif self.unit != 'Hugh':
            return
        decrement=zeros(len(self.my_stats))
        decrement[:-2].fill(-num_times)
        self.my_stats=self.my_stats+decrement


if __name__=='__main__':
    k=8
    game=str(k)
    unit='Ross'
    kwargs={}
    kwargs['game']=game
    kwargs['unit']=unit
    #x=Morph(**kwargs)
    #print(x.base_stats)
    y=dir()
    print(y)
