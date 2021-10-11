from os.path import sep

import pandas as pd

from numpy import array

from aenir2.data_dict import read_stat_names

class ZeroFiller:
    def __init__(self,game,folder=None):
        self.game=game
        self.stat_dict=read_stat_names(game)
        if folder is None:
            self.folder='.'
        elif folder == 'metadata':
            self.folder=folder
        else:
            assert type(folder) == str
            self.folder=sep.join(['.',folder,'fe%s'%game])

    def fillDict(self,stats,values):
        assert len(stats) == len(values)
        my_dict=dict()
        for old_name,new_name in self.stat_dict.items():
            if old_name in stats:
                N=stats.index(old_name)
                val=values[N]
            else:
                val=0
            if new_name:
                key=new_name
            else:
                key=old_name
            my_dict[key]=val
        return my_dict

    def fillArray(self,*args):
        values=self.fillDict(*args).values()
        values=list(values)
        values=array(values)
        return values

    def fromCSV(self,row_name,filename,valtype='Series'):
        filename=sep.join([self.folder,filename])
        data=pd.read_csv(filename,index_col=0)
        assert row_name in data.index
        row=data.loc[row_name,:]
        values=row.to_list()
        stats=tuple(row.index)
        d=self.fillDict(stats,values)
        values=tuple(d.values())
        stats=tuple(d.keys())
        data=pd.Series(data=values,index=stats,name=row_name)
        if valtype == 'array':
            x=data.to_numpy()
        elif valtype == 'Series':
            x=data
        elif valtype == 'dict':
            x=data.to_dict()
        else:
            assert valtype in ('array','Series','dict')
        return x

    def fromDict(self,d,valtype='dict'):
        assert type(d) == dict
        if valtype == 'dict':
            func=self.fillDict
        elif valtype == 'array':
            func=self.fillArray
        else:
            assert valtype in ('dict','array')
        values=tuple(d.values())
        stats=tuple(d.keys())
        return func(stats,values)

if __name__ == '__main__':
    game='6'
    unit='Roy'
    folders='raw_data'
    filename='characters_growth-rates.csv'
    x=ZeroFiller(game,folders)
    #d={'HP':99}
    #y=x.fromDict(d,valtype='array')
    y=x.fromCSV(unit,filename)
    print(y.to_dict())
