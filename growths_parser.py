import json
import pandas as pd

from random import random, randint
from numpy import zeros, array
from os.path import sep

from aenir2.scolder import scold_user

class GrowthsParser:
    def __init__(self,game):
        assert game in ('4','5')
        self.game=game
        self.game_dir=sep.join(['.','class_data','fe%s'%game])

    def inputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def growthsData(self):
        if self.game == '4':
            file='classes_growth-rates.csv'
        else:
            file='partial_growth-rates1.csv'
        growths_file=self.inputFile(file)
        growths_data=pd.read_csv(growths_file,index_col=0)
        if self.game == '5':            
            arena_patterns=['Arena (Normal)','Arena (Thief)']
            growths_data.drop(index=arena_patterns,inplace=True)
        return growths_data

    def findGrowths4(self):
        filename=self.inputFile(r'weapon-ranks.json')
        with open(filename) as rfile:
            ranks=json.load(rfile)
        physical='swords','axes','lances','bows'
        magical='fire','thunder','wind','light','dark','staves'
        bandit1='Axe Fighter','Warrior','Mountain Thief','Barbarian','Hunter','Pirate'
        ballista2='Iron Arch','Long Arch','Killer Arch'
        rank_dict=dict()
        growths_data=self.growthsData4()
        # Matches class-bases to class-growths
        for name,weapon_list in ranks.items():
            gender=None
            if ' (' in name:
                N=name.index(' (')
                gender=name[N:]
                name=name[:N]
            if name in ('Princess','Queen'):
                rank_dict[name]='Princess, Queen'
            elif name in growths_data.index:
                if gender is not None:
                    key=name+gender
                else:
                    key=name
                rank_dict[key]=name
            elif name in bandit1:
                rank_dict[name]='Bandit 1'
            elif name in ballista2:
                rank_dict[name]='Ballista 2'
            elif set.isdisjoint(set(weapon_list),set(physical)):
                rank_dict[name]='General Magical'
            elif set.isdisjoint(set(weapon_list),set(magical)):
                rank_dict[name]='General Physical'
            else:
                rank_dict[name]=None
        return rank_dict

    def writeGrowths4(self):
        rank_dict=self.findGrowths4()
        file1=self.inputFile('partial_growth-rates.json')
        file2=self.inputFile('custom-matched.csv')
        magic_and_physical=list()
        known_growths=dict()
        for key,val in rank_dict.items():
            if val is None:
                magic_and_physical.append(key)
            else:
                known_growths[key]=val
        with open(file1,'w') as wfile1:
            json.dump(known_growths,wfile1)
        with open(file2,'w') as wfile2:
            for x in magic_and_physical:
                wfile2.write(x+'\n')

    def rewriteGrowths4(self):
        growths_file=self.inputFile(r'partial_growth-rates.json')
        custom_file=self.inputFile(r'custom-matched.csv')
        all_growths=dict()
        genders={' (M)':'General Physical',' (F)':'General Magical'}
        with open(custom_file) as rfile:
            for line in rfile.readlines():
                line=line.strip()
                line=line.split(',')
                unit_class=line[0]
                if not line[1]:
                    for g,group in genders.items():
                        all_growths[unit_class+g]=group
                else:
                    all_growths[unit_class]=line[1]
        with open(growths_file) as rfile:
            known_growths=json.load(rfile)
        all_growths.update(known_growths)
        new_growths_file=self.inputFile('classes_growth-rates.json')
        with open(new_growths_file,'w') as wfile:
            json.dump(all_growths,wfile)

    def readGrowths(self):
        if self.game == '4':
            file='classes_growth-rates.json'
        elif self.game == '5':
            file='classes_growth-rates.json'
        growths_file=self.inputFile(file)
        with open(growths_file,'r') as rfile:
            d=json.load(rfile)
        return d

    def getGrowths4(self,unit_class):
        key=self.readGrowths()[unit_class]
        growths_data=self.growthsData()
        growths_row=growths_data.loc[key,:]
        return growths_row.to_numpy()

    def findGrowths5(self):
        file=self.inputFile('partial_growth-rates2.csv')
        ref_data=pd.read_csv(file,index_col=0).transpose()
        growths_dict=dict()
        growth_types='C','UC'
        ref_index=tuple(ref_data.index)
        for name in ref_data.columns:
            growths_dict[name]=dict()
            for label in growth_types:
                index_list=ref_data.index[ref_data[name] == label].to_list()
                if index_list:
                    my_indices=list()
                    for x in index_list:
                        N=ref_index.index(x)
                        my_indices.append(N)
                    growths_dict[name][label]=my_indices
        return growths_dict

    def writeGrowths5(self):
        file=self.inputFile('classes_growth-rates.json')
        with open(file,'w') as wfile:
            growths_dict=self.findGrowths5()
            json.dump(growths_dict,wfile)

    def getCommonGrowths5(self,unit_class):
        growth_dict=self.readGrowths()[unit_class]
        if 'C' not in growth_dict:
            # FE5 has nine stats with class growth rates
            return zeros(9)
        indices=growth_dict['C']
        data=self.growthsData().iloc[indices,:].to_numpy()
        if len(data) > 1:
            message='The unit class %s has more than one common growth cell.'%unit_class
            scold_user(message)
        return data[0]

    def getUncommonGrowths5(self,unit_class):
        growth_dict=self.readGrowths()[unit_class]
        increment=zeros(9)
        if 'UC' not in growth_dict:
            # FE5 has nine stats with class growth rates
            return increment
        indices=growth_dict['UC']
        if 7 in indices:
            indices.remove(7)
        data=self.growthsData().iloc[indices,:].to_numpy()
        for d in data:
            increment=increment+d
        return increment

    def getFixedGrowths5(self,unit_class):
        growth_dict=self.readGrowths()[unit_class]
        null_array=zeros(9)
        if 'UC' not in growth_dict:
            # FE5 has nine stats with class growth rates
            return null_array
        elif 7 not in growth_dict['UC']:
            return null_array
        else:
            # "...enemy/NPC characters also receive +(0-3) to each stat
            # (with equal chance), except Movement
            # (which can increase by 1 with a 10% rate)."
            # ***Assume probability is 0.125
            # ***Assume that more than one stat can level up
            rand_array=[random() for n in range(8)]
            bonus_array=[randint(1,4) for n in range(8)]
            increment=list()
            for r,b in zip(rand_array,bonus_array):
                if r <= 0.125:
                    x=b
                else:
                    x=0
                increment.append(x)
            mov_chance=random()
            if mov_chance <= 0.1:
                y=1
            else:
                y=0
            increment.append(y)
            return array(increment)

    def getGrowths5(self,unit_class,uncommon=False):
        common_growths=self.getCommonGrowths5(unit_class)
        if not all(common_growths == zeros(9)) and not uncommon:
            # If common-growths are non-zero and user wants common growths only:
            return common_growths
        uncommon_growths=self.getUncommonGrowths5(unit_class)
        fixed_growths=self.getFixedGrowths5(unit_class)
        growth_sum=common_growths+uncommon_growths+fixed_growths
        return growth_sum
        
if __name__ == '__main__':
    x=GrowthsParser('5')
    unit_class='Soldier'
    y=x.getGrowths5(unit_class)
    #y=x.growthsData()
    print(y)
