import spider, index
import time

if __name__ == '__main__':
### here to set spider start root web, format: /wiki/****
    ws = spider.wiki_spider(['/wiki/Machine_learning'])
    print(time.strftime('%Y-%m-%d %H:%M:%S'))

### here to set spider level
    ws.update_content(3)
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    im = index.IndexModule('config.ini', 'utf-8')
    im.construct_postings_lists()
    p = index.pagerank('link_file_dic.json', 'file_link_dic.json')

### here set max number of iteration of page rank calculation
    p.calculate(500)
    p.get_page_rank()