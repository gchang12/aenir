from aenir2.read_stats import *
from aenir2.gender_dict import *
from aenir2.dismount_data import DismountData

from directory_methods import messageWriter

from numpy import array, zeros

class Morph:
    def __init__(self,game,unit,lyn_mode=None,father=None):
        assert type(game) in (str,int)
        if type(game) == int:
            game=str(game)
        assert game in (str(n) for n in range(4,10))
        if unit != 'L\'Arachel':
            unit=unit.capitalize()
        if game == '4':
            kids=fe4_name_dict('child')
            if unit in kids.keys() or unit in kids.values():
                father=father.capitalize()
                father=get_true_name(game,father,fe4family='father')
        if game == '7':
            lyndis_league=character_list(game,file_match='characters_base-stats1')
            if unit in lyndis_league:
                if lyn_mode is None:
                    message='Please choose a Boolean value for the \'lyn_mode\' option.'
                    messageWriter(message)
            else:
                lyn_mode=None
        if (game,unit) == ('7','Nils'):
            unit='Ninian'
        unit=get_true_name(game,unit)
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
        self.base_levels=self.my_levels.copy()
        self.base_classes=self.my_classes.copy()
        self.my_maxes=self.maximum_stats.copy()
        self.my_stats=array(self.base_stats,dtype='float64')
        if self.game == '5':
            self.unit_info['Base Growths']=self.growth_rates.copy()
            self.unit_info['Scrolls']=list()
            dd=DismountData()
            self.unit_info['Mounted']=dd.isMounted(self.base_class)
        self.stat_names=get_stat_names(self.game)
        self.unit_info['Growths Modifier']=None
        if self.game in ('4','5'):
            self.cutoff=None
        elif self.game == '9':
            self.cutoff=3
        else:
            self.cutoff=2

    def equip_scroll(self,scroll_name=None):
        assert self.game == '5'
        assert len(self.unit_info['Scrolls']) <= 7
        scrolls=scroll_equipper()
        scrolls.columns=self.stat_names
        scroll_name=crusader_name(scroll_name)
        if scroll_name is None:
            for name in self.unit_info['Scrolls']:
                scrolls.drop(name,inplace=True)
            scrolls=scrolls.to_string()
            print(scrolls)
            return
        elif scroll_name in self.unit_info['Scrolls']:
            return
        self.unit_info['Scrolls'].append(scroll_name)
        raw_growths=array(self.unit_info['Base Growths'])
        for name in self.unit_info['Scrolls']:
            augment=scrolls.loc[name].to_numpy()
            raw_growths=raw_growths+augment
        capped_growths=list()
        for g in raw_growths:
            if g < 0:
                g=0
            capped_growths.append(g)
        self.growth_rates=array(capped_growths)

    def unequip_all_scrolls(self):
        assert self.game == '5'
        self.growth_rates=self.unit_info['Base Growths']
        self.unit_info['Scrolls'].clear()

    def history(self):
        hline='='*5
        my_levels=['Level',hline]
        my_classes=['Class',hline]
        for lv,cls in zip(self.my_levels,self.my_classes):
            if lv is None and cls is None:
                continue
            my_levels.append(lv)
            my_classes.append(cls)
        df=pd.Series(my_classes,index=my_levels)
        df=df.to_string()
        print(df)

    def modify_growths(self,mod=None):
        assert mod in ('zero','negative')
        assert self.unit_info['Growths Modifier'] is None
        if mod == 'zero':
            new_growths=zeros(len(self.stat_names),dtype='int64')
            growths_type='Zero'
        elif mod == 'negative':
            new_growths=-self.growth_rates
            growths_type='Negative'
        self.unit_info['Growths Modifier']=growths_type
        self.growth_rates=new_growths

    def dismount(self):
        assert self.can_mount()
        assert self.unit_info['Growths Modifier'] != 'Negative'
        dd=DismountData()
        decrement=dd.getBonus(self.current_class())
        if self.unit_info['Mounted']:
            x=False
        else:
            decrement=-decrement
            x=True
        self.my_stats=self.my_stats+decrement
        self.unit_info['Mounted']=x
        return self.cap_stats()

    def is_clean(self):
        conditions=(
                all(self.base_stats == self.my_stats),\
                self.base_classes == self.my_classes,\
                self.base_levels == self.my_levels
                )
        if (self.game,self.unit) == ('6','Hugh'):
            conditions=conditions[1:]
        return all(conditions)

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
        lara_promotions=(
            ['Thief Fighter','Dancer','Thief Fighter'],\
            ['Dancer','Thief Fighter']
            )
        if self.my_promotions is None:
            x=False
        elif self.unit in trainees:
            if len(self.my_classes) > 2:
                x=False
            else:
                x=True
        elif (self.game,self.unit) == ('5','Lara'):
            if self.my_classes[1:] in lara_promotions:
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
            x=self.my_classes
        index=self.current_index()
        return x[index]

    def current_class(self):
        return self.current_level(get_level=False)

    def quick_promote(self,promo_path=None):
        self.level_up('promo')
        self.promote(promo_path=promo_path)

    #   End of aforementioned methods

    def cap_stats(self):
        capped_array=list()
        for stat,limit in zip(self.my_stats,self.my_maxes):
            if stat > limit:
                stat=limit
            capped_array.append(stat)
        self.my_stats=array(capped_array)

    def level_up(self,num_levels,stat_array=None,increase_level=True,increase_stats=True):
        max_level=max_level_dict(self.game,self.current_class())
        if type(num_levels) == str:
            if num_levels.isnumeric():
                num_levels=int(num_levels)
                num_levels=num_levels-self.current_level()
            elif num_levels == 'max':
                num_levels=max_level-self.current_level()
            elif num_levels == 'promo':
                assert self.can_promote()
                mpl=self.min_promo_level(promo_path=0)
                if mpl <= self.current_level():
                    return
                else:
                    num_levels=mpl-self.current_level()
            else:
                message='\'num_levels\' must be numeric, \'max\', or \'promo\', if it is a string.'
                messageWriter(message)
        else:
            assert type(num_levels) == int
        if num_levels == 0:
            return
        else:
            assert num_levels >= 0
        if increase_level:
            assert self.current_level()+num_levels <= max_level
        if stat_array is None:
            stat_array=self.growth_rates
        if increase_level:
            index=self.current_index()
            self.my_levels[index]+=num_levels
        if increase_stats:
            self.my_stats=self.my_stats+stat_array*num_levels/100
        return self.cap_stats()

    def can_mount(self):
        if self.game == '5':
            dd=DismountData()
            return dd.isMounted(self.current_class())
        else:
            return False

    def promote(self,promo_path=None):
        assert self.can_promote()
        promo_indices=tuple(self.my_promotions.keys())
        if len(promo_indices) == 1:
            promo_path=promo_indices[0]
        elif promo_path not in promo_indices:
            print(self.my_promotions)
            return
        promo_class=self.my_promotions[promo_path]
        audit=('bases' if self.my_classes[-1] is None else 'promo')
        kwargs1={
            'class_name':self.current_class(),\
            'promo_path':promo_path,\
            'audit':audit
            }
        kwargs1.update(self.kwargs)
        promo_bonus=load_class_promo(**kwargs1).to_numpy()
        min_promo_lv=self.min_promo_level(promo_path=promo_path)
        assert self.current_level() >= min_promo_lv
        if self.can_mount():
            if not self.unit_info['Mounted']:
                self.dismount()
        self.my_stats=self.my_stats+promo_bonus

        def append_upgrade(list_var,value):
            if list_var[-1] is None:
                list_var[-1]=value
            else:
                list_var.append(value)

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
        self.my_promotions=load_class_promo_list(**kwargs2)
        if not self.can_promote():
            self.my_promotions=None
        if self.game == '5':
            can_mount=self.unit_info['Mounted']
            self.unit_info['Mounted']=self.can_mount()
            if type(can_mount) == bool and self.unit_info['Mounted'] is None:
                message=(
                    'The mounted class:',\
                    self.my_classes[0],\
                    'has promoted to an unmounted class:',\
                    self.current_class()
                    )
                messageWriter(message)
        return self.cap_stats()

    def class_level_up(self,num_levels,increase_stats,increase_level):
        kwargs={
            'class_name':self.base_class,\
            'audit':'bases'
            }
        kwargs.update(self.kwargs)
        class_growths=load_class_growths(**kwargs)
        assert class_growths is not None
        kwargs={
            'num_levels':num_levels,\
            'stat_array':class_growths.to_numpy(),\
            'increase_stats':increase_stats,\
            'increase_level':increase_level
            }
        return self.level_up(**kwargs)

    def add_hm_bonus(self,chapter=''):
        if (self.game,self.unit) == ('6','Gonzales'):
            assert all(self.my_stats == self.base_stats)
        else:
            assert self.is_clean()
        if type(chapter) == str:
            assert self.unit in hard_mode_dict().keys()
            bonus_by_chapter=hard_mode_dict()[self.unit]
            if chapter in bonus_by_chapter.keys():
                num_levels=bonus_by_chapter[chapter]
                self.unit_info['Hard Mode']=(chapter,num_levels)
            else:
                print(bonus_by_chapter)
                return
        else:
            assert type(chapter) == int
            assert chapter >= 0
            num_levels=chapter
            self.unit_info['Hard Mode']=('Custom',num_levels)
        kwargs={
            'num_levels':num_levels,\
            'increase_stats':True,\
            'increase_level':False
            }
        return self.class_level_up(**kwargs)

    def add_auto_bonus(self,chapter=''):
        if (self.game,self.unit) == ('8','Knoll'):
            # Not sure how many hidden levels are added
            # - assumed it was just one
            return self.add_hm_bonus(chapter=chapter)
        if (self.game,self.unit) == ('6','Gonzales'):
            assert self.my_levels == [5,None]
            increase_stats=False
        else:
            assert self.is_clean()
            increase_stats=True
        assert self.unit in auto_level_dict().keys()
        bonus_by_chapter=auto_level_dict()[self.unit]
        if chapter in bonus_by_chapter.keys():
            num_levels=bonus_by_chapter[chapter]
            self.unit_info['Auto-Level']=(chapter,num_levels)
        else:
            print(bonus_by_chapter)
            return
        kwargs={
            'num_levels':num_levels,\
            'increase_stats':increase_stats,\
            'increase_level':True
            }
        return self.class_level_up(**kwargs)

    def use_stat_booster(self,booster_name=None):
        bonus_dict=booster_dict(self.game)
        if booster_name is None:
            return bonus_dict
        elif booster_name in bonus_dict.keys():
            bonus=bonus_dict[booster_name]
            stat_name=bonus[0]
            increment=bonus[1]
        else:
            print(bonus_dict)
            return
        if 'Augments' not in self.unit_info.keys():
            self.unit_info['Augments']={}
        augments=self.unit_info['Augments']
        if booster_name not in augments.keys():
            augments[booster_name]=1
        else:
            augments[booster_name]+=1
        stat_loc=get_stat_names(self.game,stat_name=stat_name)
        boost_array=zeros(len(self.my_stats))
        boost_array[stat_loc:stat_loc+1].fill(increment)
        self.my_stats=self.my_stats+boost_array
        return self.cap_stats()

    def decline_hugh(self,num_times):
        assert type(num_times) == int
        assert num_times > 0
        assert (self.game,self.unit) == ('6','Hugh')
        assert self.is_clean()
        assert all(self.my_stats-num_times >= self.base_stats-3)
        assert 'Augments' not in self.unit_info.keys()
        if 'Declines' not in self.unit_info.keys():
            self.unit_info['Declines']=num_times
        else:
            self.unit_info['Declines']+=num_times
        decrement=zeros(len(self.my_stats))
        decrement[:-2].fill(-num_times)
        self.my_stats=self.my_stats+decrement

    def is_capped(self,show_df=True):
        capped_stats=self.my_stats == self.my_maxes
        d={}

        for name,val in zip(self.stat_names,capped_stats):
            d[name]=val
        if show_df:
            maxes={}
            current={}
            for name,my_stat,cap in zip(self.stat_names,self.my_stats,self.my_maxes):
                current[name]=my_stat
                maxes[name]=cap
            stat_data={
                    'capped':d,\
                    'current':current,\
                    'maximum':maxes
                    }
            df=pd.DataFrame.from_dict(stat_data)
            df=self.truncate_data(df)
            df=df.to_string()
            print(df)
        else:
            print(d)

    def stats_from_name(self,stat_name):
        stat_dict={
            'bases':self.base_stats,\
            'growths':self.growth_rates,\
            'maxes':self.my_maxes,\
            'mine':self.my_stats
            }
        return stat_dict[stat_name].copy()

    def get_short_data(self,stat_array):
        stats=self.stats_from_name(stat_array)
        kw={
            'data':stats,\
            'index':self.stat_names,\
            'name':stat_array
            }
        return pd.Series(**kw)

    def summary(self):
        columns='bases','growths'
        data_list=list()
        for name in columns:
            data=self.get_short_data(name)
            data_list.append(data)
        growths=data_list[1]
        keys=growths.index
        values=growths.values
        if self.cutoff is None:
            new_growths=['%d%%'%n for n in values]
        else:
            new_growths=list()
            k=self.cutoff
            for v in values[:-k]:
                new_growths.append('%d%%'%v)
            new_growths.extend(['-']*k)
        data_list[1]=pd.Series(data=new_growths,index=keys,name='growths')
        df=pd.DataFrame(data_list)
        df=df.transpose()
        print(df)

    def get_long_data(self,stat_array):
        my_array=self.stats_from_name(stat_array)
        data={
            'Name':self.get_display_name(),\
            'Class':self.current_class(),\
            'Level':self.current_level(),\
            '':''
            }
        for label,value in zip(self.stat_names,my_array):
            data[label]=value
        after=pd.Series(data,name=stat_array)
        return after

    def __repr__(self):
        after=self.get_long_data('mine')
        after=after.to_string()
        return after

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

    def get_display_name(self):
        display_name=[self.game,updated_name_for(self.game,self.unit)]
        if 'Father' in self.unit_info.keys():
            x=self.kwargs['father']
            x=updated_name_for(self.game,x)
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
        index_labels=self.stat_names
        cls_level={
            'Class':[self.current_class(),other.current_class(),''],\
            'Level':[self.current_level(),other.current_level(),''],\
            '':['','','']
            }
        stat_comparison=pd.DataFrame(d,index=index_labels)
        cls_level=pd.DataFrame(cls_level).transpose()
        cls_level.columns=d.keys()
        stat_comparison=self.truncate_data(stat_comparison)
        csum=sum(n for n in stat_comparison.loc[:,'diff'])
        summary={
                first_name:'',\
                second_name:'',\
                'diff':csum
                }
        blank_row={
            first_name:'',\
            second_name:'',\
            'diff':''
            }
        stat_comparison=stat_comparison.append(pd.Series(blank_row,name=''))
        stat_comparison=stat_comparison.append(pd.Series(summary,name='total'))
        stat_comparison=pd.concat([cls_level,stat_comparison]).to_string()
        print(stat_comparison)

    def truncate_data(self,data):
        if self.cutoff is None:
            x=data
        else:
            x=data.iloc[:-self.cutoff,:]
        return x

    def __call__(self):
        my_stats=list()
        print('%s\n'%self.get_display_name())
        for name,growth,avg in zip(self.stat_names,self.growth_rates,self.my_stats):
            if growth == 0:
                my_stats.append(avg)
            else:
                stat=''
                while not stat.isdigit():
                    stat=input(name+': ')
                my_stats.append(int(stat))
        stat_dict={
                    'mine':array(my_stats),\
                    'avg':self.my_stats
                    }
        stat_dict['diff']=stat_dict['mine']-stat_dict['avg']
        csum=sum(val for val in stat_dict['diff'])
        comparison=pd.DataFrame(stat_dict,index=self.stat_names)
        comparison=self.truncate_data(comparison)
        comparison=comparison.to_string()
        print('\n')
        for cls,lv in zip(self.my_classes,self.my_levels):
            if lv is None:
                continue
            if cls is None:
                continue
            print('Level %d: %s'%(lv,cls))
        print('\n',comparison)
        message=self.get_display_name(),('better' if csum >= 0 else 'worse'),abs(csum)
        message='\n\nYour %s is %s than average by %.2f points.'%message
        print(message)

if __name__=='__main__':
    k=5
    game=str(k)
    fe5_units=character_list(game)
    for unit in fe5_units:
        x=Morph(game,unit)
        x.dismount()
