import urllib2
import random
import os
#import ipdb


def retrieveIndexFile(year, qtr):
    '''
    retriece the quarterly index file from Edgar
    '''
    url = 'ftp://ftp.sec.gov/edgar/full-index/' + str(year) + '/QTR' + str(qtr) + '/master.idx'
    raw_content = urllib2.urlopen(url).readlines()
    return raw_content

def filterIndexFile(content):
    '''
    filter irrelevant content of indexfile
    reurn a list of dictionary containing the address and cik code of the company
    '''
    #ipdb.set_trace()
    filteredForms = []
    for line in content:
        line = line.rstrip('\n')
        if line[-3:] == 'txt':
            cik, name, form, date, address = line.split('|')
            if form == '10-K' or form == '10-K405':
                filteredForms.append({'cik':cik,'address':address,'date':date, 'form':form})
    return filteredForms

def randomPickForms(forms):
    '''
    randomly pick 8-K forms
    '''
    #ipdb.set_trace()
    indices = random.sample(range(len(forms)),250)
    return [forms[index] for index in indices]

def downloadForms(randomForms, year, qtr, count = 1):
    '''
    download specified forms
    '''
    
    for item in randomForms:
        url = 'ftp://ftp.sec.gov/' + item['address']
        localPath = str(year) + '_' + 'QTR' + str(qtr) + '/' + str(count) + '_' + str(year) + '_' + 'QTR' + str(qtr) + '_' + item['cik']
        with open(localPath,'w') as f_out:
            f_out.write(urllib2.urlopen(url).read())
            print 'downloaded to ' + localPath
        count += 1

def getQuarter8K(year, qtr, count = 1):
    '''
    randomly download 25 8-K forms from Edgar
    '''
    print 'processing Year: ' + str(year) + ' Quarter: ' + str(qtr) + '\n'
    if not os.path.exists((str(year) + '_' + 'QTR' + str(qtr))):
        os.makedirs((str(year) + '_' + 'QTR' + str(qtr)))


    content = retrieveIndexFile(year, qtr)

    filteredForms = filterIndexFile(content)

    #randomForms = randomPickForms(filteredForms)

    downloadForms(filteredForms, year, qtr, count)

def downloadBatch(beginYear, beginQtr, endYear, endQtr, count = 1):
    for year in range(beginYear, (endYear + 1)):
        for qtr in range(beginQtr, (endQtr + 1)):
            getQuarter8K(year, qtr, count)
            
def main():
    for year in range(1995, 2014):
        for qtr in range(1, 5):
            getQuarter8K(year, qtr, count)

#Execution
#main()
