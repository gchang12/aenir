import pandas as pd
import json

from aenir2.fetcher import Fetcher

class ClassFetcher(Fetcher):
    def __init__(self,game):
        Fetcher.__init__(self,game,'class_data','classes','')
        self.is_jugdral=self.game in ('4','5')

    def scrapeBases(self):
        skip_col=(2 if self.game in ('5','9') else 1)
        kw={
            'section':'base-stats',\
            'parser':'html.parser',\
            'skip_col':skip_col
            }
        return Fetcher.scrapePage(self,**kw)

    def recordData(self,stat_type):
        if stat_type == 'base-stats':
            page_list=list(self.scrapeBases())
        elif stat_type == 'growth-rates':
            if self.is_jugdral:
                return
            else:
                page_list=list(self.scrapeGrowths())
        filename='classes_%s.csv'%stat_type
        file=self.outputFile(filename)
        kw={'index':False,'header':False}
        if len(page_list) == 1:
            data=page_list[0]
            h=False
        else:
            headers=page_list[0].iloc[0,:].to_list()
            new_data=list()
            for data in page_list:
                new_data.append(data[1:])
            data=pd.concat(new_data)
            h=headers
        kw['header']=h
        data.to_csv(file,**kw)

    def recordBases(self):
        self.recordData('base-stats')

    def scrapeGrowths(self):
        if self.is_jugdral:
            return
        kw={
            'section':'growth-rates',\
            'parser':'html.parser',\
            'skip_col':None
            }
        return Fetcher.scrapePage(self,**kw)

    def recordGrowths(self):
        self.recordData('growth-rates')

    def recordGrowths4(self):
        assert self.game == '4'
        soup=self.boilSoup('growth-rates')
        table=list()
        headers=list()
        for tr in soup.find_all('tr'):
            if not headers:
                for th in tr.find_all('th'):
                    headers.append(th.text.strip())
                table.append(headers)
                continue
            row=list()
            for td in tr.find_all('td'):
                cell=td.text
                if '*' in cell:
                    cell=cell.replace('*','')
                elif cell.isdigit():
                    cell=int(cell)
                row.append(cell)
            table.append(row)
        df=pd.DataFrame(table)
        filename=self.outputFile('partial_growth-rates.csv')
        df.to_csv(filename,index=False,header=False)

    def recordGrowths5(self):
        soup=self.boilSoup('growth-rates')
        tables=list()
        get_filename=lambda x:'partial_growth-rates'+str(x)+'.csv'
        for n,table in enumerate(soup.find_all('table')):
            if n == 1:
                continue
            contents=list()
            headers=list()
            for tr in table.find_all('tr'):
                if not headers:
                    for th in tr.find_all('th'):
                        headers.append(th.text.strip())
                    contents.append(headers)
                    continue
                row=list()
                for td in tr.find_all('td'):
                    cell=td.text
                    a=td.find('a')
                    if cell.isdigit():
                        cell=int(cell)
                    elif a is not None:
                        img=a.find('img')
                        cell=('UC' if img['alt'] == 'Uncommon' else 'C')
                    row.append(cell)
                contents.append(row)
            tables.append(contents)
        for n,t in enumerate(tables,start=1):
            filename=get_filename(n)
            data=pd.DataFrame(t)
            filename=self.outputFile(filename)
            data.to_csv(filename,index=False,header=False)

def test_all(func):
    for n in range(4,10):
        n=str(n)
        func(n)

def save(n,stat_type):
    x=ClassFetcher(n)
    if stat_type == 'bases':
        x.recordBases()
    elif stat_type == 'growths':
        x.recordGrowths()

def save_growthsJ(n):
    assert n in (4,5)
    n=str(n)
    x=ClassFetcher(n)
    if n == '4':
        x.recordGrowths4()
    else:
        x.recordGrowths5()

def save_bases(n):
    save(n,'bases')

def save_growths(n):
    save(n,'growths')

if __name__ == '__main__':
    func=save_bases
    func('5')
