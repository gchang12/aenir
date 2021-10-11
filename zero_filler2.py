from os.path import sep

import pandas as pd

from numpy import array

from aenir2.data_dict import read_stat_names

class ZeroFiller:
    def __init__(self,game,folder=None):
        assert type(folder) in (type(None),tuple,str)
        self.game=game
        self.stat_dict=read_stat_names(game)
        if folder is None:
            self.folder='.'
        elif type(folder) == tuple:
            self.folder=sep.join(folder)
        elif folder == 'metadata':
            self.folder=folder
        else:
            self.folder=sep.join(['.',folder,'fe%s'%game])

    def fillDict(self,stats,values):
        if (type(stats),type(values)) == (str,int):
            stats=(stats,)
            values=(values,)
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

    def fromCSV(self,row_name,filename,return_as='Series'):
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
        if return_as == 'array':
            x=data.to_numpy()
        elif return_as == 'Series':
            x=data
        elif return_as == 'dict':
            x=data.to_dict()
        else:
            assert return_as in ('array','Series','dict')
        return x

    def fromDict(self,d,return_as='dict'):
        assert type(d) == dict
        if return_as == 'dict':
            func=self.fillDict
        elif return_as == 'array':
            func=self.fillArray
        else:
            assert return_as in ('dict','array')
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
    #y=x.fromDict(d,return_as='array')
    y=x.fromCSV(unit,filename)
    print(y.to_dict())
