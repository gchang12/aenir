from aenir2.fetcher import Fetcher
from os import sep

class ItemFetcher(Fetcher):
    def __init__(self,game):
        Fetcher.__init__(self,game,'weapon_data','inventory','data-locations.txt')
        self.page_contents=None
        self.table_titles=list()

    def createDir(self):
        Fetcher.createDir(self)

    def joinUrl(self,section=None):
        return Fetcher.joinUrl(self,section)

    def outputFile(self,filename):
        return Fetcher.outputFile(self,filename)

    def gatherRows(self,tr,cell):
        return Fetcher.gatherRows(self,tr,cell)

    def scrapeTable(self,table):
        return Fetcher.scrapeTable(self,table)

    def boilSoup(self,section,parser):
        return Fetcher.boilSoup(self,section,parser)

    def gatherUrl(self):
        game=self.title
        url=self.joinUrl()
        soup=BeautifulSoup(get(url).text,'html.parser')
        unneeded_pages=(
            'Items','Crusader Scrolls','Monster Weapons','Accessories'
            )
        url_contents=list()
        for a in soup.find_all('a'):
            if 'href' not in a.attrs:
                continue
            href=a['href']
            if 'inventory' not in href:
                if url_contents:
                    break
                else:
                    continue
            title=a.text
            if title in unneeded_pages:
                continue
            N=len(game)+len('inventory')+2
            href=href[N:]
            href=href.replace('/','')
            url_contents.append(href)
        return url_contents

    def recordUrl(self):
        url_contents=self.gatherUrl()
        with open(self.data_file,'a') as wfile:
            wfile.write(self.game+',')
            for portal in url_contents:
                wfile.write(portal+',')
            wfile.write('\n')

    def retrieveUrl(self):
        with open(self.data_file,'r') as rfile:
            for line in rfile.readlines():
                line=line.split(',')
                if line[0] != self.game:
                    continue
                return line[1:-1]

    def scrapePage(self,section):
        if (self.game,section) in [('5','axes'),('6','anima-tomes')]:
            parser='html5lib'
        else:
            parser='html.parser'
        self.page_contents=list(Fetcher.scrapePage(self,section,parser=parser))
        # Differs from original script in the respect that it pings SF.net twice
        soup=self.boilSoup(section,parser)
        if len(self.page_contents) > 1:
            for h3 in soup.find_all('h3'):
                title=h3.text
                if ' ' in title:
                    N=title.index(' ')
                    title=title[:N]
                title=title.lower()
                self.table_titles.append(title)
        if not self.table_titles:
            self.table_titles.append(None)
        page_dict=dict()
        for content,title in zip(self.page_contents,self.table_titles):
            page_dict[title]=content
        return page_dict

    def recordPage(self,section):
        page_dict=self.scrapePage(section)
        kw={'index':False,'header':False}
        for label,data in page_dict.items():
            if label is None:
                if '-tomes' in section:
                    N=section.index('-tomes')
                    section=section[:N]
                elif 'laguz' in section:
                    section='laguz'
                filename=section+'.csv'
            else:
                filename=label+'.csv'
            file=self.outputFile(filename)
            data.to_csv(file,**kw)

    def recordAllPages(self):
        url_list=self.retrieveUrl()
        for url in url_list:
            self.recordPage(url)

def save_all():
    for n in range(4,10):
        game=str(n)
        dog=ItemFetcher(game)
        dog.recordAllPages()

if __name__ == '__main__':
    x=ItemFetcher('4')
    print(x.game_dir)
