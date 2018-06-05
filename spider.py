import urllib.request
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import json
import re

def get_news_pool(root, start, end):
    news_pool = []
    for i in range(start,end,-1):
        page_url = ''
        if i != start:
            page_url = root +'_%d.shtml'%(i)
        else:
            page_url = root + '.shtml'
        try:
            response = urllib.request.urlopen(page_url)
        except Exception as e:
            print("-----%s: %s-----"%(type(e), page_url))
            continue
        html = response.read()
        soup = BeautifulSoup(html,"lxml") # http://www.crummy.com/software/BeautifulSoup/bs4/doc.zh/
        td = soup.find('td', class_ = "newsblue1")
        a = td.find_all('a')
        span = td.find_all('span')
        for i in range(len(a)):
            date_time = span[i].string
            url = a[i].get('href')
            title = a[i].string
            news_info = ['2016-'+date_time[1:3]+'-'+date_time[4:-1]+':00',url,title]
            news_pool.append(news_info)
    return(news_pool)

def crawl_news(url, levels, link_file_dic):
    if levels == 0:
        return
    connect = urllib.request.urlopen(url)
    content = connect.read()
    time.sleep(2)
    soup = BeautifulSoup(content, 'lxml')
    print(soup.prettify)
    # todo add url to dic
    link_file_dic[url] = 0
    pass #################################

    if levels != 1:
        # todo find next level's links
        a = soup.find_all('a')
        nextlevel = []
        for each in a:
            s = each.get('class')
            if s == ['link-home']:
                l = each.get('href')
                if l.startswith('//w'):
                    l = 'http:' + l
                elif l.startswith('/a'):
                    l = 'http://www.sohu.com' + l
                nextlevel.append(l)

        print(nextlevel)
        for each in nextlevel:
            if each in link_file_dic:
                continue
            crawl_news(each, levels-1, link_file_dic)
                


    return


# rooturl = ['https://en.wikipedia.org/wiki/Machine_learning']
# # rooturl = ['http://m.sohu.com/ch/8?_f=m-article_ch']
# # rooturl = ['http://m.sohu.com/a/234071193_162758?_f=m-channel_8_focus_3']
# # testurl = 'http://www.sohu.com/a/233949131_267106?_f=index_chan08news_1'
# links = []
# link_file_dic = {}

class wiki_spider:
    def __init__(self, rooturl):
        self.rooturl = rooturl
        self.link_file_dic = {}
        self.url_head = 'https://en.wikipedia.org'
        self.web_count = 0
    
    def update_content(self, level, extendurl = None):
        if extendurl is not None and type(extendurl) is list:
            self.rooturl.extend(extendurl)
        self.link_file_dic = {}
        for eachurl in self.rooturl:
            self._crawl_content(eachurl, level)
        self.save_link_file_dic()

    def save_link_file_dic(self):
        with open('link_file_dic.json', 'w') as f:
            json.dump(self.link_file_dic, f)

    def _crawl_content(self, url, level):
        # if level == 0:
        #     return
        if url.startswith(self.url_head):
            complete_url = url
            url = complete_url[len(self.url_head):]
        elif url.startswith('/wiki/'):
            complete_url = self.url_head + url
        else:
            return
        print(complete_url)
        connection = urllib.request.urlopen(complete_url)
        content = connection.read()
        time.sleep(1)
        soup = BeautifulSoup(content, 'lxml')
        # print(soup.prettify)
        content = soup.body.find('div', id='content')
        title = content.find('h1').string
        print(title, url)
        # print(content.find('div'))
        main_body = content.find('div', id='bodyContent').find('div', id='mw-content-text').find('div')
        paragraphs = main_body.find_all('p')
        text = ''
        for eachgraph in paragraphs:
            parastr = ''
            for string in eachgraph.strings:
                parastr += string
            # parastr = parastr.replace(u'\xa0', u' ')
            text = text + parastr + '\n'
        
        filename = 'data/%d.txt' %self.web_count
        with open(filename, 'w', encoding='utf8') as f:
            f.write(text)
            self.web_count += 1

        a = []
        for each in paragraphs:
            a.extend(each.find_all('a', title=re.compile('.+')))
        links = []
        for each in a:
            links.append(each.get('href'))

        self.link_file_dic[url] = [filename, links] # [content file name, links it points to].
        
        if level == 1:
            return

        for each in links:
            if each in self.link_file_dic:
                continue
            self._crawl_content(each, level-1)

        return
            
            



if __name__ == '__main__':
    ws = wiki_spider(['/wiki/Machine_learning'])
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    ws.update_content(3)
    print(time.strftime('%Y-%m-%d %H:%M:%S'))

# for eachurl in rooturl:
#     connect = urllib.request.urlopen(eachurl)
#     content = connect.read()
#     time.sleep(1)
#     # print(content)

#     soup = BeautifulSoup(content, 'lxml')
#     # print(soup.title)

#     h4 = soup.find_all('h4')
#     for each in h4:
#         link = each.find(target = "_blank")
#         if link is not None:
#             l = 'http:' + link.get('href')
#             links.append(l)
#             link_file_dic[l] = 0
#     # print(soup.prettify)

# for each in links:
#     print(each)
#     crawl_news(each, 5, link_file_dic)
#     break

    
