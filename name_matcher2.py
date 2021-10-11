import json

from os.path import sep

from aenir2.gender_dict import gender_dict

class NameMatcher:
    def __init__(self,game,unit):
        folder=sep.join(['.','class_data'])
        filePointer=lambda x: sep.join([folder,'fe%s'%game,x])
        dict_file=filePointer('class_dict.json')
        rank_file=filePointer('weapon-ranks.json')

        self.game=game
        self.unit=unit
        self.gender=gender_dict(game)[unit]
        self.name_dict=self.fetchDict(dict_file)
        self.rank_dict=self.fetchDict(rank_file)

    def fetchDict(self,filename):
        with open(filename,'r') as rfile:
            d=json.load(rfile)
        return d

    def fetchName(self,unit_class):
        if 'Wagon' in self.gender:
            return
        unit_classG=unit_class+self.gender
        ranks=self.rank_dict.keys()
        if self.game in ('7','8'):
            lord_list='Eliwood','Hector','Lyn','Ephraim','Eirika'
            if self.unit in lord_list:
                return 'Lord (%s)'%self.unit
        if unit_class in ranks:
            return unit_class
        elif unit_classG in ranks:
            return unit_classG
        else:
            if unit_class not in self.name_dict.keys():
                return
            new_class=self.name_dict[unit_class]
            new_classG=new_class+self.gender
            if new_class in ranks:
                return new_class
            elif newclassG in ranks:
                return new_classG

    def fetchRanks(self,unit_class):
        if self.game == '9':
            weapon_dict={
                'Sword':'swords',\
                'Lance':'lances',\
                'Axe':'axes',\
                'Bow':'bows'
                }
            for key in weapon_dict.keys():
                if key in unit_class:
                    return [key]
        ranks=self.rank_dict.keys()
        proper_name=self.fetchName(unit_class)
        if proper_name is None:
            return []
        else:
            usable_weapons=self.rank_dict[proper_name]
            return usable_weapons
