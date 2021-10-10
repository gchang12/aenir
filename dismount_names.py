from aenir2.name_lists import get_stat_names
from aenir2.data_dict import read_stat_names

from os.path import sep

import pandas as pd

class DataDict3:
    def __init__(self,game):
        self.stat_dir=sep.join(['.','raw_data','fe5'])
        filePointer=lambda x: sep.join([self.stat_dir,x+'.csv'])
        self.promo_file=filePointer('classes_promotion-gains')
        self.bases_file=filePointer('characters_base-stats')
        self.dismount_file=sep.join(['.','metadata','fe5-dismount.csv'])
        self.file_dict={
            'promo':self.promo_file,\
            'bases':self.bases_file,\
            'dismount':self.dismount_file
            }

    def getNameList(self,file=None):
        filename=self.file_dict[file]
        data=pd.read_csv(filename,index_col=0)
        if file in ('promo','bases'):
            if file == 'promo':
                column='Promotion'
            else:
                column='Class'
            return data.loc[:,column].to_list()
        else:
            return list(data.index)

    def isMounted(self,unit_class):
        if unit_class in self.getNameList(file='dismount'):
            return True
        else:
            return None

    def getBonus(self,unit_class):
        filename=self.file_dict['dismount']
        data=pd.read_csv(filename,index_col=0)
        row=data.loc[unit_class,:]
        return row.to_numpy()

    def dismountDiff(self):
        dismount_list=self.getNameList('dismount')
        promo_list=self.getNameList('promo')
        bases_list=self.getNameList('bases')
        diff=list()
        for x in dismount_list:
            if x in promo_list:
                continue
            elif x in bases_list:
                continue
            else:
                diff.append(x)
        return diff

if __name__ == '__main__':
    x=DataDict3()
    file='dismount'
    unit_class='Lance Knight'
    y=x.getBonus(unit_class)
    print(y)
