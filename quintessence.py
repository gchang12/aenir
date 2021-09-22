from aenir2.read_stats import *
from aenir2.gender_dict import *
from dir_manager import dir_switcher

from numpy import array, zeros
from copy import deepcopy

class Morph:
    """
    Retrieves virtual copy of character stats and return object containing stats.
    :param game: The game the unit is from.
    :param unit: The name of the unit, as used by SerenesForest.net.
    :param lyn_mode: FE7 only; specifies whether to retrieve Lyn Mode stats for unit, if applicable.
    :param father: FE4 only; specifies father of child unit.

    game='6'
    unit='Roy'
    our_boy=Morph(game,unit)
    """
    def __init__(self,game,unit,lyn_mode=False,father='Arden'):
        dir_switcher('aenir2')
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
        promo_dict=self.my_promotions
        if len(promo_dict) > 1:
            promo_class=promo_dict[promo_path]
        else:
            promo_class=tuple(promo_dict.values())[0]
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
        """
        Increase unit level and apply bonuses based on personal growths.
        :param num_levels: Number of levels to add to character's current level.

        game='6'
        unit='Roy'
        our_boy=Morph(game,unit)

        num_levels=19
        our_boy.level_up(num_levels)
        """
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
        """
        Levels up unit to promotion level if necessary and upgrades unit class.
        :param promo_path: The code for the class the unit upgrades to. See ``promotions'' attribute.

        game='6'
        unit='Roy'
        our_boy=Morph(game,unit)

        our_boy.promote()
        """
        if not self.can_promote():
            return
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
        """
        Appends hard-mode bonus to applicable characters.
        :param num_levels: Specify number of hidden level-ups manually; overrides ``chapter'' parameter.
        :param chapter: Specify chapter character is recruited on, if it affects bonuses.

        game='6'
        unit='Cath'
        chapter='16'
        cath=Morph(game,unit)
        cath.add_hm_bonus(chapter=chapter)
        """
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
        return self.class_level_up(**kwargs)

    def add_auto_bonus(self,chapter=''):
        """
        Adds levels to applicable unit and appends stat bonuses based on class-growths.
        :param chapter: The chapter the unit is recruited on.

        game='8'
        unit='Amelia'
        chapter='13'
        bad_in_general=Morph(game,unit)
        bad_in_general.add_auto_bonus(chapter)
        """
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
        """
        Appends stat bonus to argument as specified by by item; varies from game to game.
        :param stat_name: The name of the stat to boost.
        """
        bonus_dict=booster_dict(self.game,get_bonus=True)
        bonus=bonus_dict[stat_name]
        stat_loc=get_stat_names(self.game,stat_name=stat_name)
        boost_array=zeros(len(self.my_stats))
        boost_array[stat_loc:stat_loc+1].fill(bonus)
        self.my_stats=self.my_stats+boost_array
        self.cap_stats()

    def decline_hugh(self,num_times):
        """
        Decrements Hugh's stats according to the number of times you decline him.
        :param num_times: Number of times you decline to hire him in FE6.
        """
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
        stat_array=zip(get_stat_names(self.game),self.my_stats,other.my_stats)
        assert len(get_stat_names(self.game)) == len(self.my_stats)

        def update_colors(key,f1,f2):
            if f1() == f2():
                x=None
            else:
                x=True
            colors[key]=x

        update_colors('Class',self.current_class,other.current_class)
        update_colors('Level',self.current_level,other.current_level)

        for name,my_stat,other_stat in stat_array:
            if my_stat == other_stat:
                x=None
            else:
                x=my_stat > other_stat
            colors[name]=x
        return colors

    def is_capped(self):
        """
        Returns dictionary of which stats the unit has capped.
        """
        capped_stats=self.my_stats == self.my_maxes
        stat_names=get_stat_names(self.game)
        d={}

        for name,val in zip(stat_names,capped_stats):
            d[name]=val

        return d

    def __repr__(self):
        stat_labels=get_stat_names(self.game)
        stat_values=self.my_stats
        data={
            'Name':self.get_display_name(),\
            'Class':self.current_class(),\
            'Level':self.current_level(),\
            '':''
            }
        for label,value in zip(stat_labels,stat_values):
            data[label]=value
        return pd.Series(data).to_string()

    def max_level(self):
        args=(self.game,self.current_class())
        max_level=max_level_dict(*args)
        return max_level

    def __eq__(self,other):
        conditions=(
            all(self.my_stats == other.my_stats),\
            self.my_levels == other.my_levels,\
            self.my_classes == other.my_classes,\
            self.kwargs == other.kwargs
            )
        return all(conditions)

    def __neq__(self,other):
        return not self.__eq__(other)

    def get_display_name(self):
        display_name=[self.game,self.unit]
        if 'Father' in self.unit_info.keys():
            x=self.kwargs['father']
        elif 'Lyn Mode' in self.unit_info.keys():
            if self.kwargs['lyn_mode']:
                x='LM'
            else:
                x=''
        else:
            x=''
        if x:
            display_name.insert(1,x)
        return '!'.join(display_name)

    def __sub__(self,other):
        gba_games=('6','7','8')
        if self.game in gba_games:
            assert other.game in gba_games
            zero_growth_stat='Con'
        else:
            assert self.game == other.game
            if self.game == '9':
                zero_growth_stat='Mov'
            else:
                zero_growth_stat=None
        diff=self.my_stats-other.my_stats
        first=self.my_stats
        second=other.my_stats
        first_name=self.get_display_name()
        second_name=other.get_display_name()
        if first_name == second_name:
            first_name+='-1'
            second_name+='-2'
        d={
            first_name:first,\
            second_name:second,\
            'diff':diff
            }
        index_labels=get_stat_names(self.game)
        stat_comparison=pd.DataFrame(d,index=index_labels)
        if zero_growth_stat is not None:
            cutoff_row=tuple(stat_comparison.index).index(zero_growth_stat)
            stat_comparison=stat_comparison.iloc[:cutoff_row,:]
        csum=sum(n for n in stat_comparison.loc[:,'diff'])
        return stat_comparison,csum

    def __call__(self):
        stat_labels=get_stat_names(self.game)
        my_stats=()
        print('%s\n'%self.get_display_name())
        for name,growth,avg in zip(stat_labels,self.growth_rates,self.my_stats):
            if growth == 0:
                my_stats+=(avg,)
            else:
                stat=''
                while not stat.isdigit():
                    stat=input(name+': ')
                my_stats+=(int(stat),)
        stat_dict={}
        stat_dict['mine']=array(my_stats)
        stat_dict['avg']=self.my_stats
        stat_dict['diff']=stat_dict['mine']-stat_dict['avg']
        comparison=pd.DataFrame(stat_dict,index=stat_labels)
        print('\n')
        for cls,lv in zip(self.my_classes,self.my_levels):
            if lv is None:
                continue
            if cls is None:
                continue
            print('Level %d: %s\n'%(lv,cls))
        print(comparison)


if __name__=='__main__':
    k=4
    game=str(k)
    unit='Tinny'
    x=Morph(game,unit)
    print(x.my_promotions)
    x.promote(1)
    print(x)
