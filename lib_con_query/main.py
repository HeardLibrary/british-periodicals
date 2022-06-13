from curses import raw
import sruthi
import pandas as pd
import sys
import time
import re
import os
en_dataframe = '/Users/tojo/Desktop/text_analysis_vanderbilt/gutenberg/metadata/en_metadata.csv'
BASE = 'http://lx2.loc.gov:210/LCDB?' #the url to the library of congress database
full_data = {'pgid':[], 'title':[], 'author':[], 'pub_year':[], 'pub_region':[]} # where the collected data is stored
raw_data = []

# reads the csv file containing the book titles to be processed
def readfile(path):
    df = pd.read_csv(path)
    return df

# access each title and quere them one at a time
def get_data():
    df = readfile(en_dataframe)
    titles = list(df.title)
    authors = df.author
    ids = list(df.id)
    for i in range(len(titles)):
        title = titles[i]
        title = re.sub(".:,", "", title)
        # the query either returns a server error or an empty result if the keyword is to long. so I have to cut the long titles
        # and only get the first 4 words
        if len(title.split()) > 3:
            title = " ".join(title.split(" ")[:4])
        id = ids[i]
        author = authors[i]
        data_search(repr(title), BASE, id, author)
        process_data(raw_data, repr(titles[i]), id, author)
        print('{} books processed out of {}'.format(i, len(titles))) # to track the progress
        print('pgid: ' + str(len(full_data['pgid'])) + " ==> " + str(full_data['pgid'][-1]))
        print('title: ' + str(len(full_data['title']))+ " ==> " + str(full_data['title'][-1]))
        print('author: ' + str(len(full_data['author']))+ " ==> " + str(full_data['author'][-1]))
        print('pub_year: ' + str(len(full_data['pub_year']))+ " ==> " + str(full_data['pub_year'][-1]))
        print('pub_region' + str(len(full_data['pub_region']))+ " ==> " + str(full_data['pub_region'][-1]))
    makefile(full_data)
    print('data collection completed. New file saved as full_metadata.csv')




# this is where the query is processed
def data_search(title, base, id, author):
    global raw_data
    raw_data = []
    count = 0
    # I skip the books that may return any error. I will evaluate the result at the end to see the percentage of non-processed books
    # try:
    records = sruthi.searchretrieve(base, query=title, sru_version=1.1)
    if records.count > 50:
        records = records[:50]
    # each record in the records has a different data value (it may be due to a book having multiple editions), so we have to
    # go through all the records and find the earliest release. But some queries return 100's or 1000's of records, so a single
    # query may take minutes or even hours to complete, which is not time efficient. So, I decided to only search through the
    # first 20 records of any query that have more than 50 records. This is subject ot change depending on my evaluation of the result
    for record in records:
        if count == 30:
            time.sleep(3)
            count = 0
        fields = record.get('datafield', [])
        for field in fields:
            if field['tag'] == '260': #this the publication and distribution tag. year and region/country of publication are found here
                try:
                    if len(field.get('subfield', [])) > 0:
                        year = (field['subfield'][-1]['text'])
                        region = (field['subfield'][0]['text'])
                        raw_data.append([region, year])
                        print(raw_data)
                        # if temp != '' and len(temp) == 4:
                        #     year = int(temp)
                        # if pub_dist != None and pub_dist > year:
                        #     pub_dist = year
                        #     rec = record
                        # elif pub_dist == None:
                        #     pub_dist = year
                except Exception as e:
                    pass
        count += 1
    # process_data(raw_data, title, id, author)
    # if rec != None:
    #     fields = rec.get('datafield', [])
    #     for field in fields:
    #         if field['tag'] == '260':
    #             if len(field.get('subfield', [])) > 0:
    #                 temp = (field['subfield'])
    #                 if type(temp) == list:
    #                     region = temp[0]['text']
    #                 else:
    #                     region = temp


    # except Exception as e:
    #     pass
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