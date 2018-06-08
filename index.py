import os
# import xml.etree.ElementTree as ET
# import jieba
import sqlite3
import configparser
import time
import re
import json
import numpy as np
# import random

def low_case_doc(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
        text = text.lower()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)
    return

def preprocess(config_path, config_encoding):
    config = configparser.ConfigParser()
    config.read(config_path, config_encoding)
    # print(config['DEFAULT']['doc_dir_path'])
    files = os.listdir(config['DEFAULT']['doc_dir_path'])
    # print(files)
    for each in files:
        low_case_doc(config['DEFAULT']['doc_dir_path'] + each)

class pagerank:
    def __init__(self, link_file_dic_filename, out_file_link_filename):
        with open(link_file_dic_filename, 'r') as f:
            self.link_file_dic = json.load(f)  # [title, content file name, links it points to].
            # print(self.link_file_dic)

        out_file_link = {}
        for eachkey in self.link_file_dic:
            docid = self.link_file_dic[eachkey][1]
            out_file_link[docid] = eachkey
        # print(out_file_link)

        with open(out_file_link_filename, 'w') as f:
            json.dump(out_file_link, f)

        self.in_link_dic = {}
        for eachkey in self.link_file_dic:
            self.in_link_dic[eachkey] = set()
        
        for eachkey in self.link_file_dic:
            for eachlink in self.link_file_dic[eachkey][2]:
                if eachlink not in self.in_link_dic:
                    # self.in_link_dic[eachlink] = set()
                    continue
                self.in_link_dic[eachlink].add(eachkey)

        self.whole_link = list(self.link_file_dic.keys())
        self.whole_link.sort(key=lambda x: int(self.link_file_dic[x][1]))
        # print(self.whole_link)
        print(len(self.whole_link))
        self.link_num = len(self.whole_link)
        self.pagerank_value = {}
        self.pagerank_value_array = np.tile(np.array([1/self.link_num]), (self.link_num, 1))
        for each in self.whole_link:
            self.pagerank_value[each] = 1/self.link_num
        # print(self.pagerank_value)
        self.adjacencyM = np.zeros((self.link_num, self.link_num))
        for i in range(self.link_num):
            link = self.whole_link[i]
            point_to = self.link_file_dic[link][2]
            if len(point_to) == 0:
                continue
            v = 1/len(point_to)
            for each in point_to:
                if each not in self.link_file_dic:
                    continue
                p_column = i
                p_row = int(self.link_file_dic[each][1])
                self.adjacencyM[p_row, p_column] = v

        self.random_walk = np.tile(np.array([1/self.link_num]), (self.link_num, 1))

        self.alpha = 0.85
        self.adjacencyM = self.alpha * self.adjacencyM
        self.random_walk = (1 - self.alpha) * self.random_walk

        return

    def calculate(self, max_round):
        print('start tuning page_rank_value...........')
        for i in range(max_round):
            last = self.pagerank_value_array
            self.pagerank_value_array = np.dot(self.adjacencyM, last) + self.random_walk
            stable = np.sum((self.pagerank_value_array - last)**2)
            print('change in round', i+1,': ', stable)
            if stable == 0:
                break
        print('done!')      
        # print(self.pagerank_value_array)

        return

    def get_page_rank(self):
        for each in self.pagerank_value:
            self.pagerank_value[each] = self.pagerank_value_array[int(self.link_file_dic[each][1]), 0]
        # print(self.pagerank_value_array.reshape((-1)).tolist())
        pagerank_json = {'link_dic':self.pagerank_value, 'list':self.pagerank_value_array.reshape((-1)).tolist()}
        # print(self.pagerank_value[self.whole_link[0]],self.pagerank_value[self.whole_link[1]],self.pagerank_value[self.whole_link[2]])
        with open('page_rank_v.json', 'w') as f:
            json.dump(pagerank_json, f)
            
        return self.pagerank_value_array

class Doc:
    docid = 0
    date_time = ''
    tf = 0
    ld = 0
    def __init__(self, docid, date_time, tf, ld):
        self.docid = docid
        self.date_time = date_time
        self.tf = tf
        self.ld = ld
    def __repr__(self):
        return(str(self.docid) + '\t' + self.date_time + '\t' + str(self.tf) + '\t' + str(self.ld))
    def __str__(self):
        return(str(self.docid) + '\t' + self.date_time + '\t' + str(self.tf) + '\t' + str(self.ld))

class IndexModule:
    stop_words = set()
    postings_lists = {}
    
    config_path = ''
    config_encoding = ''
    
    def __init__(self, config_path, config_encoding):
        self.config_path = config_path
        self.config_encoding = config_encoding
        config = configparser.ConfigParser()
        config.read(config_path, config_encoding)
        f = open(config['DEFAULT']['stop_words_path'], encoding = config['DEFAULT']['stop_words_encoding'])
        words = f.read()
        self.stop_words = set(words.split('\n'))

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
        
    def clean_list(self, seg_list):
        cleaned_dict = {}
        n = 0
        for i in seg_list:
            i = i.strip().lower()
            if i != '' and not self.is_number(i) and i not in self.stop_words:
                n = n + 1
                if i in cleaned_dict:
                    cleaned_dict[i] = cleaned_dict[i] + 1
                else:
                    cleaned_dict[i] = 1
        return n, cleaned_dict
    
    def write_postings_to_db(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute('''DROP TABLE IF EXISTS postings''')
        c.execute('''CREATE TABLE postings
                     (term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')

        for key, value in self.postings_lists.items():
            doc_list = '\n'.join(map(str,value[1]))
            t = (key, value[0], doc_list)
            c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

        conn.commit()
        conn.close()
    
    def construct_postings_lists(self):
        config = configparser.ConfigParser()
        config.read(self.config_path, self.config_encoding)
        files = os.listdir(config['DEFAULT']['doc_dir_path'])
        AVG_L = 0
        for i in files:
            print('processing file: ' + i)
            with open(config['DEFAULT']['doc_dir_path'] + i, 'r', encoding='utf-8') as f:
                date_time = f.readline().strip()  ### if spider record time, uncomment this line
                title = f.readline().strip()
                body = f.read()
                docid = int(i[:-4])
                # date_time = time.strftime('%Y-%m-%d %H:%M:%S')  ## simulate different file's spider time, it should be collect in spider.py
                seg_list = re.findall(r'[A-Za-z]+', title + ' ' + body)
           
            
            ld, cleaned_dict = self.clean_list(seg_list)
            
            AVG_L = AVG_L + ld
            
            for key, value in cleaned_dict.items():
                d = Doc(docid, date_time, value, ld)
                if key in self.postings_lists:
                    self.postings_lists[key][0] = self.postings_lists[key][0] + 1 # df++
                    self.postings_lists[key][1].append(d)
                else:
                    self.postings_lists[key] = [1, [d]] # [df, [Doc]]
        AVG_L = AVG_L / len(files)
        config.set('DEFAULT', 'N', str(len(files)))
        config.set('DEFAULT', 'avg_l', str(AVG_L))
        with open(self.config_path, 'w', encoding = self.config_encoding) as configfile:
            config.write(configfile)
        
        print('Processing done! Inverted index is generated')
        print('writing inverted index into database......')
        self.write_postings_to_db(config['DEFAULT']['db_path'])
        print('done!')


if __name__ == '__main__':
    # preprocess('config.ini', 'utf-8')
    im = IndexModule('config.ini', 'utf-8')
    im.construct_postings_lists()
    p = pagerank('link_file_dic.json', 'file_link_dic.json')
    p.calculate(500)
    p.get_page_rank()
    