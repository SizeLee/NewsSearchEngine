import os
# import xml.etree.ElementTree as ET
# import jieba
import sqlite3
import configparser
import time
import re

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
        return

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
                # date_time = f.readline().strip()  ### if spider record time, uncomment this line
                title = f.readline().strip()
                body = f.read()
                docid = int(i[:-4])
                date_time = time.strftime('%Y-%m-%d %H:%M:%S')  ## simulate different file's spider time, it should be collect in spider.py
                seg_list = re.findall(r'[A-Za-z]+', title + ' ' + body)
            # root = ET.parse(config['DEFAULT']['doc_dir_path'] + i).getroot()
            # title = root.find('title').text
            # body = root.find('body').text
            # docid = int(root.find('id').text)
            # date_time = root.find('datetime').text
            # seg_list = jieba.lcut(title + '。' + body, cut_all=False)
            
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
    