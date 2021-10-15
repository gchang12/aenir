import pandas as pd
import json

from os.path import sep, exists

from aenir2.zero_filler2 import ZeroFiller

class ClassMatcher:
    def __init__(self,game):
        assert game in (str(n) for n in range(5,10))
        self.game=game
        self.game_dir=sep.join(['.','class_data','fe%s'%game])
        self.bases_file=self.inputFile('classes_base-stats.csv')
        if self.game == '5':
            suffix='.json'
        else:
            suffix='.csv'
        self.growths_file=self.inputFile('classes_growth-rates'+suffix)
        kw={
            'index_col':0
            }
        self.bases_data=pd.read_csv(self.bases_file,**kw)
        if self.game == '5':
            with open(self.growths_file,'r') as rfile:
                self.growths_data=json.load(rfile)
        else:
            self.growths_data=pd.read_csv(self.growths_file,**kw)

    def inputFile(self,filename):
        return sep.join([self.game_dir,filename])

    def outputFile(self,filename):
        return sep.join(['.','audit','fe%s'%self.game,filename])

    def rawNameList(self):
        if self.game == '5':
            growth_names=(self.growths_data.keys())
        else:
            growth_names=(self.growths_data.index)
        bases_names=(self.bases_data.index)
        return bases_names,growth_names

    def basesVsGrowths(self):
        bases_names,growth_names=self.rawNameList()
        unmatched=set()
        matched=dict()
        for name in bases_names:
            gen_name=None
            if ' (' in name:
                gen_name=name
                N=name.index(' (')
                name=name[:N]
            if name in growth_names:
                if gen_name is not None:
                    key=gen_name
                else:
                    key=name
                matched[key]=name
            elif gen_name in growth_names:
                matched[gen_name]=gen_name
            else:
                if gen_name is None:
                    entry=name
                else:
                    entry=gen_name
                unmatched.add(entry)
        return matched,unmatched

    def growthsVsBases(self):
        bases_names,growth_names=self.rawNameList()
        unmatched=set()
        matched=dict()
        for name in growth_names:
            gen_name=None
            if ' (' not in name:
                gen_name=name+' ('
                N=len(gen_name)
            for other_name in bases_names:
                if name == other_name:
                    matched[name]=name
                elif gen_name is not None and gen_name == other_name[:N]:
                    matched[name]=other_name
            if name not in matched.keys():
                unmatched.add(name)
        return matched,unmatched

    def compileNameDict(self):
        bases_dict=self.inputFile('partial-matches1.json')
        with open(bases_dict,'r') as rfile:
            name_dict=json.load(rfile)
        dict_file=self.inputFile('bases-to-growths.csv')
        if not exists(dict_file):
            return name_dict
        with open(dict_file,'r') as rfile:
            for line in rfile.readlines():
                line=line.strip()
                line=line.split(',')
                bases_name=line[0]
                growths_name=line[1]
                if not growths_name:
                    continue
                name_dict[bases_name]=growths_name
                if ' (' not in bases_name:
                    genders=' (M)',' (F)'
                    for g in genders:
                        name_dict[bases_name+g]=growths_name
        return name_dict

    def saveNameDict(self):
        name_dict=self.compileNameDict()
        file='name_dict.json'
        file=self.inputFile(file)
        with open(file,'w') as wfile:
            json.dump(name_dict,wfile)

    def recordMatches(self,vs='bases-vs-growths'):
        if vs == 'bases-vs-growths':
            file1='1'
            name_list=self.basesVsGrowths()
        elif vs == 'growths-vs-bases':
            file1='2'
            name_list=self.growthsVsBases()
        matched,unmatched=name_list
        file1=self.inputFile('partial-matches%s.json'%file1)
        file2=self.outputFile('%s.txt'%vs)
        with open(file1,'w') as wfile:
            json.dump(matched,wfile)
        with open(file2,'w') as wfile:
            for z in unmatched:
                wfile.write(z+'\n')

    def getGrowths(self,unit_class):
        name_dict=self.compileNameDict()
        row=name_dict[unit_class]
        zf=ZeroFiller(self.game)
        data=zf.fromDF(row,self.growths_data)
        return data

def test_all(func):
    for i in range(5,10):
        i=str(i)
        func(i)

def compare(n):
    x=ClassMatcher(n)
    x.recordMatches('bases-vs-growths')
    x.recordMatches('growths-vs-bases')

def save_dict(n):
    x=ClassMatcher(n)
    x.saveNameDict()

if __name__ == '__main__':
    func=save_dict
    test_all(func)
