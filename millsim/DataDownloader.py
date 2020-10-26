# -*- coding: utf-8 -*-
import requests 
import hashlib
import os 

MILLIMIL_ENDPOINT = "http://gavo.mpa-garching.mpg.de/Millennium/MyDB"
CACHE_DIRECTORY   = "cache"

class DataDownloader:
    """DataDownloader, downloads CSV from SQL queries"""
    
    def ensure_numeric(self, value, what):
        if not isinstance(value, int) and not isinstance(value, float):
            raise Exception(what + " is not a valid numeric argument")
        
    def __init__(self, maxEntries = 1000):
        self.maxEntries = maxEntries
        self.csv = []
        self.rows = []
        self.column_names = []
        self.column_data = {}
        self.set_query("""
            select * from millimil..MPAHalo
            where snapnum=50
            and np between 100 and 1000
            and x between 10 and 20
            and y between 10 and 20
            and z between 10 and 20
            """)
        
        if not os.path.isdir(CACHE_DIRECTORY):
            if os.path.exists(CACHE_DIRECTORY):
                raise Exception("Cache directory exists, but it is not a file?")
            
            try:
                os.mkdir(CACHE_DIRECTORY)
            except OSError as e:
                raise Exception(\
                    "Failed to create cache directory " + CACHE_DIRECTORY +\
                    ": " + e.strerror())
        
    def set_query(self, query):
        self.query = query
        self.queryHash = hashlib.md5(self.query.encode("utf-8")).digest().hex()
        self.compose_post_data()
        
    def compose_post_data(self):
        self.postData = {
            'action': 'doQuery', 
            'queryMode':'stream', 
            'batch':'false', 
            'SQL':self.query,
            'MAXROWS':self.maxEntries
        }

    def load_from_cache(self):
        f = open(CACHE_DIRECTORY + "/" + self.queryHash + ".csv", "r")
        return f.read()
        
    def store_to_cache(self, text):
        f = open(CACHE_DIRECTORY + "/" + self.queryHash + ".csv", "w")
        f.write(text)
        
    def process_data(self):
        self.column_data = {}
        self.column_names = []
        self.rows = []
        
        if len(self.csv) < 1:
            raise Exception("Missing column information (bad query?)")
        
        for name in self.csv[0]:
            self.column_names.append(name)
            self.column_data[name] = []
            
        try:
            for i in range(1, len(self.csv)):
                rowdata = self.csv[i]
                self.rows.append(rowdata)
                for j in range(len(self.column_names)):
                    col = self.column_names[j]
                    
                    try:
                        self.column_data[col].append(float(rowdata[j]))
                    except:
                        self.column_data[col].append(rowdata[j])
                
        except:
            raise Exception("SQL data format exception, call your local guru")

            
    def download(self):
        self.csv = []
        try:
            csvresult = self.load_from_cache()
        except:
            r = requests.post(url = MILLIMIL_ENDPOINT, data = self.postData)
            r.raise_for_status()
            csvresult = r.text
            self.store_to_cache(csvresult)
            
        for line in csvresult.splitlines():
            if line[0] != '#':
                self.csv.append(line.split(','))
                
        self.process_data()
        return self.csv

    def row_count(self):
        return len(self.rows)
    
    def column(self, column):
        return self.column_data[column]
    
    def row(self, row):
        return self.rows[row]
        