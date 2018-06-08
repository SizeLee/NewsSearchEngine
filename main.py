from flask import Flask, render_template, request, redirect

from search_engine import SearchEngine

# import xml.etree.ElementTree as ET
import sqlite3
import configparser
import time, json

# import jieba

app = Flask(__name__)

doc_dir_path = ''
db_path = ''
global page
global keys


def init():
    config = configparser.ConfigParser()
    config.read('config.ini', 'utf-8')
    global dir_path, db_path, url_head
    dir_path = config['DEFAULT']['doc_dir_path']
    db_path = config['DEFAULT']['db_path']
    url_head = config['DEFAULT']['url_head']


@app.route('/')
def main():
    init()
    return render_template('search.html', error=True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods=['POST'])
def search():
    try:
        global keys
        global checked
        checked = ['checked="true"', '', '']
        keys = request.form['key_word']
        #print(keys)
        if keys not in ['']:
            print(time.clock())
            flag,page = searchidlist(keys)
            # print(1)
            if flag==0:
                return render_template('search.html', error=False)
            # print(2)
            docs = cut_page(page, 0)
            print(time.clock())
            return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                                   error=True)
        else:
            return render_template('search.html', error=False)

    except:
        print('search error')


def searchidlist(key, selected=0):
    global page
    global doc_id
    se = SearchEngine('config.ini', 'utf-8')
    flag, id_scores = se.search(key, selected)
    # 返回docid列表
    doc_id = [i for i, s in id_scores]
    # print(flag, flag)
    page = []
    for i in range(1, (len(doc_id) // 10 + 2)):
        page.append(i)
    return flag,page


def cut_page(page, no):
    docs = find(doc_id[no*10:page[no]*10])
    # print(docs)
    return docs


# 将需要的数据以字典形式打包传递给search函数
def find(docid, extra=False):
    docs = []
    global dir_path, db_path, url_head
    with open('file_link_dic.json' , 'r') as f:
        id_link_dic = json.load(f)
    # print(id_link_dic)
    for id in docid:
        # root = ET.parse(dir_path + '%s.xml' % id).getroot()
        with open(dir_path + '%s.txt' % id, encoding = 'utf-8') as f:
            url = url_head + id_link_dic[str(id)]
            datetime = f.readline().strip()
            title = f.readline().strip()
            body = f.read()
            snippet = body[0:120] + '……'
            time = datetime.split(' ')[0]
            
        doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': datetime, 'time': time, 'body': body,
               'id': id, 'extra': []}
        # if extra:  ###recommendation
        #     temp_doc = get_k_nearest(db_path, id)
        #     for i in temp_doc:
        #         root = ET.parse(dir_path + '%s.xml' % i).getroot()
        #         title = root.find('title').text
        #         doc['extra'].append({'id': i, 'title': title})
        docs.append(doc)
    return docs


@app.route('/search/page/<page_no>/', methods=['GET'])
def next_page(page_no):
    try:
        page_no = int(page_no)
        docs = cut_page(page, (page_no-1))
        return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
                               error=True)
    except:
        print('next error')


@app.route('/search/<key>/', methods=['POST'])
def high_search(key):
    try:
        selected = int(request.form['order'])
        for i in range(3):
            if i == selected:
                checked[i] = 'checked="true"'
            else:
                checked[i] = ''
        flag,page = searchidlist(key, selected)
        if flag==0:
            return render_template('search.html', error=False)
        docs = cut_page(page, 0)
        return render_template('high_search.html',checked=checked ,key=keys, docs=docs, page=page,
                               error=True)
    except:
        print('high search error')


@app.route('/search/<id>/', methods=['GET', 'POST'])
def content(id):
    try:
        doc = find([id], extra=True)
        # return render_template('content.html', doc=doc[0])
        return redirect(doc[0]['url'])
    except:
        print('content error')


def get_k_nearest(db_path, docid, k=5):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM knearest WHERE id=?", (docid,))
    docs = c.fetchone()
    #print(docs)
    conn.close()
    return docs[1: 1 + (k if k < 5 else 5)]  # max = 5


if __name__ == '__main__':
    # jieba.initialize()  # 手动初始化（可选）
    app.run()
