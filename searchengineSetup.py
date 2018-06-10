import spider, index
import time

if __name__ == '__main__':
    ws = spider.wiki_spider(['/wiki/Machine_learning'])
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    ws.update_content(3)### here to set spider level
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    im = index.IndexModule('config.ini', 'utf-8')
    im.construct_postings_lists()
    p = index.pagerank('link_file_dic.json', 'file_link_dic.json')
    p.calculate(500)### here set max number of iteration of page rank calculation
    p.get_page_rank()