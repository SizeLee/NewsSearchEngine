import urllib.request
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import json
import re

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
        # print(complete_url)
        connection = urllib.request.urlopen(complete_url)
        content = connection.read()
        time.sleep(1)
        soup = BeautifulSoup(content, 'lxml')
        # print(soup.prettify)
        content = soup.body.find('div', id='content')
        title = soup.title.string
        print(title, url)
        # print(content.find('div'))
        main_body = content.find('div', id='bodyContent').find('div', id='mw-content-text').find('div')
        paragraphs = main_body.find_all('p')
        text = title + '\n'
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

    
