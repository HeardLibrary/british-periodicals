from curses import raw
import sruthi
import pandas as pd
import sys
import time
import re
import os
en_dataframe = '/Users/tojo/Desktop/text_analysis_vanderbilt/gutenberg/metadata/en_metadata.csv'
BASE = 'http://lx2.loc.gov:210/LCDB?' #the url to the library of congress database
full_data = {'pgid':[], 'title':[], 'author':[], 'pub_year':[], 'pub_region':[], 'original_publication': []} # where the collected data is stored
raw_data = []
org_year = None
# reads the csv file containing the book titles to be processed
def readfile(path):
    df = pd.read_csv(path)
    return df

# access each title and quere them one at a time
def get_data():
    df = readfile(en_dataframe)
    titles = list(map(str, list(df.title)))
    authors = list(map(str, df.author))
    ids = list(df.id)
    for i in range(len(titles)):
        title = titles[i]
        id = ids[i]
        author = authors[i]
        data_search(repr(title), BASE, id, author)
        process_data(raw_data, repr(titles[i]), id, author)
        full_data['original_publication'].append(org_year)
        print('{} books processed out of {}'.format(i, len(titles))) # to track the progress
        print('pgid: ' + str(len(full_data['pgid'])) + " ==> " + str(full_data['pgid'][-1]))
        print('title: ' + str(len(full_data['title']))+ " ==> " + str(full_data['title'][-1]))
        print('author: ' + str(len(full_data['author']))+ " ==> " + str(full_data['author'][-1]))
        print('pub_year: ' + str(len(full_data['pub_year']))+ " ==> " + str(full_data['pub_year'][-1]))
        print('pub_region: ' + str(len(full_data['pub_region']))+ " ==> " + str(full_data['pub_region'][-1]))
        print('original_publication: ' + str(len(full_data['original_publication']))+ " ==> " + str(full_data['original_publication'][-1]))
    makefile(full_data)
    print('data collection completed. New file saved as full_metadata.csv')




# this is where the query is processed
def data_search(title, base, id, author):
    global raw_data
    global full_data
    global org_year
    raw_data = []
    org_year = None
    count = 0
    temp_record = True
    title = re.sub('.:', '', title)
    # I skip the books that may return any error. I will evaluate the result at the end to see the percentage of non-processed books
    try:
        records = sruthi.searchretrieve(base, query=title, sru_version=1.1)
        if records.count > 100:
            records = records[:100]
        for record in records:
            if count == 20:
                time.sleep(3)
                count = 0
            fields = record.get('datafield', [])
            for field in fields:
                if field['tag'] == '100': #this the publication and distribution tag. year and region/country of publication are found here
                    try:
                        if len(field.get('subfield', [])) > 0:
                            get_author = (field['subfield'][0]['text'][:-1])
                            print(get_author + ' = ' + author)
                            if author == get_author:
                                for field in fields:
                                    if field['tag'] == '260': #this the publication and distribution tag. year and region/country of publication are found here
                                        try:
                                            if len(field.get('subfield', [])) > 0:
                                                year = (field['subfield'][-1]['text'])
                                                region = (field['subfield'][0]['text'])
                                                raw_data.append([region, year]) 
                                                print(raw_data) 
                                        except Exception as e:
                                            pass
                                    if field['tag'] == '500': #this the publication and distribution tag. year and region/country of publication are found here
                                        try:
                                            if len(field.get('subfield', [])) > 0:
                                                raw_temp = (field['subfield'])
                                                if type(raw_temp) == list:
                                                    org_year = raw_temp[-1]['text']
                                                else:
                                                    org_year = raw_temp['text']
                                        
                                        except Exception as e:
                                            pass
                                
                    except Exception as e:
                        pass
           
            
               
    except sruthi.errors.SruError:
        pass
    except sruthi.errors.SruthiError:
        time.sleep(3)
        data_search(title, base, id, author)
        count += 1
    os.system('cls' if os.name == 'nt' else 'clear')

    
def process_data(data, title, id, author):
    global full_data
    region = None
    rec = None
    pub_year = None
    years = [i[-1] for i in data]
    for i in years:
        if len(re.sub('\D', '', i)) == 4:
            if pub_year is None:
                pub_year = int(re.sub('\D', '', i))
            elif pub_year > int(re.sub('\D', '', i)):
                pub_year = int(re.sub('\D', '', i))
        elif len(re.sub('\D', '', i)) > 4:
            if pub_year is None:
                pub_year = int(re.sub('\D', '', i)[:4])
            elif pub_year > int(re.sub('\D', '', i)[:4]):
                pub_year = int(re.sub('\D', '', i)[:4])
        if '[' in i and ']' in i:
            temp = i[i.index('['):i.index(']')]
            temp = re.sub('\D', '', temp)
            if temp != '':
                if pub_year is None or pub_year > int(temp) and len(temp) == 4:
                    pub_year = int(temp)
    for i in data:
        for j in i:
            if pub_year != None and str(pub_year) in j:
                region = i[0]
    full_data['pgid'].append(id)
    full_data['title'].append(title)
    full_data['author'].append(author)
    full_data['pub_year'].append(pub_year)
    full_data['pub_region'].append(region)


def makefile(data):
    path = '/Users/tojo/Desktop/text_analysis_vanderbilt/gutenberg/metadata/full_metadata.csv'
    df = pd.DataFrame.from_dict(data)
    df.to_csv(path)

get_data()