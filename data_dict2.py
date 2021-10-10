import json
import pandas as pd
import re

from os import walk, mkdir
from os.path import sep, exists

class DataDict2:
    def __init__(self,game):
        self.game=game
        self.stat_dir=sep.join(['.','raw_data','fe%s'%self.game])
        self.item_file=sep.join(['.','weapon_ranks','fe%s.json'%self.game])
        self.junk_dir=sep.join(['.','junk_dir'])
        self.output_dir=sep.join([self.junk_dir,'fe%s'%self.game])
        self.json_dir=sep.join(['.','not-in'])
        self.json_output_dir=sep.join([self.json_dir,'fe%s'%self.game])
        my_directories=(self.junk_dir,self.output_dir,self.json_dir,self.json_output_dir)
        for folder in my_directories:
            if not exists(folder):
                mkdir(folder)
        with open(self.item_file,'r') as rfile:
            self.main_names=tuple(json.load(rfile))
        self.non_matches=dict()
        self.checklist={
            'bases':'characters_base-stats',\
            'promo':'classes_promotion-gains'
            }
        self.promo_file=sep.join([self.stat_dir,self.checklist['promo']+'.csv'])

    def matchNames(self,checklist,file):
        matched=list()
        for check in checklist:
            x=re.match(check,file)
            x=bool(x)
            matched.append(x)
        return any(matched)

    def compareNames(self,file,return_set=False):
        newfile=sep.join([self.stat_dir,file])
        data=pd.read_csv(newfile,index_col=0)
        if 'characters' in file:
            stat_classes=data.loc[:,'Class'].to_list()
        else:
            stat_classes=list(data.index)
            if self.game != '7':
                promo_list=data.loc[:,'Promotion'].to_list()
                stat_classes.extend(promo_list)
        if return_set:
            return set(stat_classes)
        non_matches=list()
        for name in self.main_names:
            if name not in stat_classes:
                non_matches.append(name)
        self.non_matches[file]=non_matches

    def saveNonMatches(self):
        for key,values in self.non_matches.items():
            key=key[:-4]+'.txt'
            filename=sep.join([self.output_dir,key])
            with open(filename,'w') as wfile:
                for val in values:
                    wfile.write(val+'\n')

    def listFromFile(self,file):
        file=sep.join([self.output_dir,file])
        my_list=list()
        with open(file,'r') as rfile:
            for line in rfile.readlines():
                line=line.strip()
                my_list.append(line)
        return my_list

    def mergeBaseNonMatches(self,return_set=False):
        pattern=self.checklist['bases']
        match_list=list()
        for x,y,filelist in walk(self.output_dir):
            if len(filelist) <= 2:
                return
            num_dups=len(filelist)-1
            for file in filelist:
                if re.match(pattern,file):
                    base_matches=self.listFromFile(file)
                    match_list.extend(base_matches)
        new_list=list()
        other_list=list()
        for element in match_list:
            count=match_list.count(element)
            if count == num_dups:
                new_list.append(element)
            else:
                other_list.append(element)
        if return_set:
            return set(other_list)
        else:
            return new_list

    def saveToJSON(self,filename,iterable):
        if '.txt' in filename:
            filename=filename.replace('.txt','.json')
        filename=sep.join([self.json_output_dir,filename])
        with open(filename,'w') as wfile:
            json.dump(iterable,wfile)

    def firstMerge(self):
        # Compiles names in bases and in promo, then converts to JSON
        base=self.checklist['bases']+'.txt'
        if self.mergeBaseNonMatches is None:
            base_list=self.listFromFile(base)
        else:
            base_list=self.mergeBaseNonMatches()
        promo=self.checklist['promo']+'.txt'
        promo_list=self.listFromFile(promo)
        base='bases.json'
        promo='promo.json'
        self.saveToJSON(base,base_list)
        self.saveToJSON(promo,promo_list)

    def setFromJSON(self,name):
        if '.json' not in name:
            name=name+'.json'
        name=sep.join([self.json_output_dir,name])
        with open(name,'r') as rfile:
            name=json.load(rfile)
        if name is None:
            return set()
        else:
            return set(name)

    def secondMerge(self):
        # Returns everything in bases, promo, and in intersection
        base=self.setFromJSON('bases')
        promo=self.setFromJSON('promo')
        base_and_promo=set.intersection(base,promo)
        only_promo=promo-base_and_promo
        only_base=base-base_and_promo
        filelist='base-and-promo','bases-only','promo-only'
        setlist=base_and_promo,only_base,only_promo
        for file,s in zip(filelist,setlist):
            file=file+'.json'
            if not s:
                s=None
            else:
                s=tuple(s)
            self.saveToJSON(file,s)

    def thirdMerge(self,subtract=None):
        # Returns elements in #1 that are not in #2
        assert subtract in ('bases','promo')
        if subtract == 'bases':
            add='promo'
        else:
            add='bases'
        filename='%s-minus-%s.json'%(add,subtract)
        add_classes=self.setFromJSON('%s-only'%add)
        kw={
            'file':self.checklist[subtract]+'.csv',\
            'return_set':True
            }
        try:
            sub_classes=self.compareNames(**kw)
        except FileNotFoundError:
            sub_classes=self.mergeBaseNonMatches(return_set=True)
        set_diff=add_classes-sub_classes
        if not set_diff:
            set_diff=None
        else:
            set_diff=list(set_diff)
        self.saveToJSON(filename,set_diff)

    def checkClassNames(self):
        checklist=tuple(self.checklist.values())
        for x,y,filelist in walk(self.stat_dir):
            if not filelist:
                continue
            for file in filelist:
                is_correct_file=self.matchNames(checklist,file)
                if not is_correct_file:
                    continue
                self.compareNames(file)
        self.saveNonMatches()

if __name__ == '__main__':
    for n in range(4,10):
        game=str(n)
        x=DataDict2(game)
        x.thirdMerge(subtract='bases')
        x.thirdMerge(subtract='promo')
