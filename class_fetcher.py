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
            page_list=self.scrapeBases()
        elif stat_type == 'growth-rates':
            if self.is_jugdral:
                return
            else:
                page_list=self.scrapeGrowths()
        filename='classes_%s.csv'%stat_type
        file=self.outputFile(filename)
        kw={'index':False,'header':False}
        for data in page_list:
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

def test_all(func):
    for n in range(4,10):
        n=str(n)
        func(n)

def save_bases(n):
    x=ClassFetcher(n)
    func=x.recordBases()

def save_growths(n):
    x=ClassFetcher(n)
    func=x.recordGrowths()

if __name__ == '__main__':
    func=save_bases
    test_all(func)
