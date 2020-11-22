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

    def cap_stats(self,stat_array=None):
        capped_array=()
        if stat_array is None:
            stat_array=self.my_stats
        for stat,limit in zip(stat_array,self.my_maxes):
            if stat > limit:
                stat=limit
            capped_array+=(stat,)
        stat_array=array(capped_array)
        return stat_array

    def stat_forecast(self,increment):
        old_stats=self.my_stats.copy()
        new_stats=old_stats+increment
        new_stats=self.cap_stats(new_stats)
        return old_stats,new_stats

    def level_up(self,num_levels,stat_array=None,increase_level=True,increase_stats=True,get_forecast=False):
        #   Check if valid action - IMPORT TO TKINTER
        max_level=max_level_dict(self.game,self.current_level(get_level=False))
        if self.current_level() >= max_level:
            return
        if self.current_level() + num_levels > max_level:
            num_levels=max_level-self.current_level()
        if stat_array is None:
            stat_array=self.growth_rates
        if get_forecast:
            forecast_level=self.current_level()+num_levels
            level_info={
                'Level':forecast_level
                }
            if increase_stats:
                increment=stat_array*num_levels/100
            else:
                increment=zeros(len(self.my_stats))
            return self.stat_forecast(increment),level_info
        if increase_level:
            index=self.current_index()
            self.my_levels[index]+=num_levels
        if increase_stats:
            self.my_stats=self.my_stats+stat_array*num_levels/100
        self.cap_stats()

    def promote(self,promo_path=0,get_forecast=False):
        #   Check if valid action - IMPORT TO TKINTER
        if not self.can_promote():
            return
        #   Correcting promotion path here - IMPORT TO TKINTER
        promo_indices=tuple(self.my_promotions.keys())
        if len(promo_indices) == 1:
            promo_path=promo_indices[0]
        promo_class=self.my_promotions[promo_path]
        kwargs0={
            'game':self.game,\
            'unit':self.unit,\
            'unit_class':promo_class
            }
        min_promo_lv=promo_level_dict(**kwargs0)
        audit=('bases' if self.my_classes[-1] is None else 'promo')
        kwargs1={
            'class_name':self.current_level(get_level=False),\
            'promo_path':promo_path,\
            'audit':audit
            }
        kwargs1.update(self.kwargs)
        promo_bonus=load_class_promo(**kwargs1).to_numpy()
        if self.game == '4':
            reset_level=self.current_level()
        else:
            reset_level=1
        num_levels=min_promo_lv-self.current_level()
        if get_forecast:
            if num_levels < 0:
                num_levels=0
            forecast=self.stat_forecast(promo_bonus)
            promoted_info={
                'Level':reset_level,\
                'Class':promo_class
                }
            unpromoted_info={
                'Level':self.current_level()+num_levels,\
                'Class':self.current_level(get_level=False)
                }
            return forecast,promoted_info,unpromoted_info
        #   Checks if unit can promote at current level
        #   -if no, automatically levels up unit
        #   -IMPORT TO TKINTER
        if self.current_level() < min_promo_lv:
            self.level_up(num_levels)
        self.my_stats=self.my_stats+promo_bonus

        def append_upgrade(list_var,value):
            if list_var[-1] is None:
                list_var[-1]=value
            else:
                list_var+=[value]

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

    def class_level_up(self,num_levels,increase_stats,increase_level,get_forecast):
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
            'increase_level':increase_level,\
            'get_forecast':get_forecast
            }
        return self.level_up(**kwargs)

    def add_hm_bonus(self,num_levels=None,chapter='',get_forecast=False):
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
            'increase_level':False,\
            'get_forecast':get_forecast
            }
        return self.class_level_up(**kwargs)

    def add_auto_bonus(self,chapter='',get_forecast=False):
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
            'increase_level':True,\
            'get_forecast':get_forecast
            }
        return self.class_level_up(**kwargs)

    def use_stat_booster(self,stat_name,get_forecast=False):
        bonus_dict=booster_dict(self.game,get_bonus=True)
        bonus=bonus_dict[stat_name]
        stat_loc=stat_names(self.game,stat_name=stat_name)
        boost_array=zeros(len(self.my_stats))
        boost_array[stat_loc:stat_loc+1].fill(bonus)
        if get_forecast:
            forecast=self.stat_forecast(boost_array)
            return forecast
        self.my_stats=self.my_stats+boost_array
        self.cap_stats()

    def decline_hugh(self,num_times,get_forecast=False):
        #   Check if valid action - IMPORT TO TKINTER
        if num_times not in range(4):
            return
        elif self.unit != 'Hugh':
            return
        decrement=zeros(len(self.my_stats))
        decrement[:-2].fill(-num_times)
        if get_forecast:
            forecast=self.stat_forecast(decrement)
            return forecast
        self.my_stats=self.my_stats+decrement


if __name__=='__main__':
    k=4
    game=str(k)
    unit='Levin'
    kwargs={}
    kwargs['game']=game
    kwargs['unit']=unit
    x=Morph(**kwargs)
    print(x.unit_info)
    print(x.base_stats)
