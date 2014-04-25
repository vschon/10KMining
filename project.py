import numpy as np
import pandas as pd
import os
import re
import datetime as dt
from dateutil.parser import parse
import ipdb
import urllib2
import ipdb
import sys

class Form10Fetcher:

    def __init__(self):
        self.cikDict = loadCikCusipMap()
 
    def retrieveIndexFile(self, year, qtr):
        '''
        retriece the quarterly index file from Edgar
        '''
        url = 'ftp://ftp.sec.gov/edgar/full-index/' + str(year) + '/QTR' + str(qtr) + '/master.idx'
        raw_content = urllib2.urlopen(url).readlines()
        return raw_content

    def filterIndexFile(self, content):
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
                    try:
                        cik = cik.zfill(10)
                        self.cikDict[cik]
                        filteredForms.append({'cik':cik,'address':address,'date':date, 'form':form})
                    except:
                        pass
        return filteredForms

    def downloadForms(self, randomForms, year, qtr, count = 1):
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

    def getQuarter10K(self, year, qtr, count = 1):
        '''
        download 10-K forms from Edgar
        '''
        print 'processing Year: ' + str(year) + ' Quarter: ' + str(qtr) + '\n'
        if not os.path.exists((str(year) + '_' + 'QTR' + str(qtr))):
            os.makedirs((str(year) + '_' + 'QTR' + str(qtr)))


        content = self.retrieveIndexFile(year, qtr)

        filteredForms = self.filterIndexFile(content)

        #randomForms = randomPickForms(filteredForms)

        self.downloadForms(filteredForms, year, qtr, count)

    def downloadBatch(self, beginYear, beginQtr, endYear, endQtr, count = 1):
        for year in range(beginYear, (endYear + 1)):
            for qtr in range(beginQtr, (endQtr + 1)):
                try:
                    self.getQuarter10K(year, qtr, count)
                except:
                    print "\n########################################\n"
                    print "Download 10K forms for Year " + str(year) + " Qtr: " + str(qtr) + " Failed!\n"
                    print "Please restart at " + str(year) + " Qtr " + str(qtr) + " !\n\n"
                    sys.exit()
                print "Successfully Download 10K forms for Year " + str(year) + " Qtr: " + str(qtr) + "\n\n"

                
    def downloader(self):
        for year in range(1995, 2014):
            for qtr in range(1, 5):
                self.getQuarter10K(year, qtr, count)


def getCIKList(beginYear, beginQtr, endYear,endQtr):
    '''
    Get non-duplicated cik from all 8-K forms
    '''
    cikDatePath = 'CIK_Date_Table.csv'
    
    for year in range(beginYear, (endYear+1)):
        for qtr in range(beginQtr, (endQtr+1)):
            dir_addr = str(year) + '_QTR' + str(qtr)
            fileList = os.listdir(dir_addr)
            for K8File in fileList:
                K8Path = os.path.join(dir_addr, K8File)
                with open(K8Path) as f:
                    for line in f.readlines():
                        if 'FILED AS OF DATE' in line:
                            match  = re.search(r'\d\d\d\d\d\d\d\d',line)
                            date = match.group(0)
                            cik = K8File.split('_')[3]
                            output = date + '|' + cik + '\n'
                            with open(cikDatePath, 'a') as f_out:
                                f_out.write(output)
                                print output

def getCIKSet():
    '''
    Extract distinct cik code for mapping to cusip
    '''
    cikDatePath = 'CIK_Date_Table.csv'
    cikSetPath = 'CIK_Set.csv'
    with open(cikDatePath, 'r') as f:
        cikDateList = f.readlines()
        cikList = [cik_date.split('|')[1] for cik_date in cikDateList]
        cikSet = set(cikList)
    with open(cikSetPath, 'a') as f_out:
        #ipdb.set_trace()
        for cik in cikSet:
            f_out.write(cik)


def CIK_CUSIP_Map():
    '''
    generate the mapping file from cik to cusip
    '''
    compustatPath = 'compustat2.csv'
    cik_cusipMapPath = 'CIK_CUSIP_map.csv'
    cikSet = set() 
    with open(compustatPath) as f:
        content = f.readlines()
        for i in range(len(content)):
            if i > 0:
                lineSplit = content[i].split(',')
                cik = lineSplit[5]
                cusip = lineSplit[4]
                if cik in cikSet:
                    pass
                else:
                    with open(cik_cusipMapPath, 'a') as f_out:
                        f_out.write((cik.rstrip('\n') + '|' + cusip + '\n'))
                        print cik.rstrip('\n') + '|' + cusip
                    cikSet.add(cik)


def loadCikCusipMap():
    '''
    return the cik - cusip dictionary
    '''
    cik_cusipMapPath = 'CIK_CUSIP_map.csv'
    cikCusipMap = {}

    with open(cik_cusipMapPath, 'r') as mapFile:
        allMappings = mapFile.readlines()
        for mapEntry in allMappings:
            cik, cusip = mapEntry.split('|')
            cusip = cusip.rstrip('\n')
            cikCusipMap[cik] = cusip
    return cikCusipMap


def generateMasterFile():
    '''
    generate cik, date and cusip
    '''
    cikDatePath = 'CIK_Date_Table.csv'
    masterPath = 'Master.idx'

    #load CIK CUSIP mapping
    cikCusipMap = loadCikCusipMap() 

    with open(cikDatePath,'r') as f:
        files = f.readlines()
        for line in files:
            date, cik = line.split('|')
            cik = cik.rstrip('\n').zfill(10)
            #ipdb.set_trace()
            try:
                cusip = cikCusipMap[cik]
                with open(masterPath, 'a') as master:
                    master.write(date + ',' + cik + ',' + cusip + '\n')
            except:
                pass

           

def generateStockDB():
    '''
    Partition the big CRSP DB into small file indexed by cusip
    '''
    crspPath = 'crsp.csv'
    testPath = 'test'

    cikCusipMap = loadCikCusipMap()

    i = 1
    with open(crspPath) as f:
        while True:
            line = f.readline()
            i += 1
            if line == '':
                break
            else:
                item = line.split(',') 
                cusip = item[0]
                savePath = 'crsp/' + cusip[:6] + '.csv'
                with open(savePath, 'a') as f_out:
                    f_out.write(line)
            if i%1000 == 0:
                print i

def loadSPReturn():
    '''
    load sp composite return into memory, stored as pandas dataframe
    '''
    sp = pd.read_csv('SPReturn.csv', index_col = 'DATE', parse_dates = True)
    return sp

def loadStockReturn(cusip):
    '''
    load stock return specified by key cusip
    
    Parameters:
        cusip: first number of cusip code
    Returns:
        {'State': 1 if time series found, otherwise 0
        'data': the data frame of the series
    '''
    #if cusip == '524908100':
    #ipdb.set_trace()
    if len(cusip) < 6:
        print 'cusip length < 6!'
        return {"state":0}
    cusip = cusip[:6]
    filePath = 'crsp/' + cusip + '.csv' 
    if not os.path.exists(filePath):
        print 'CUSIP: ' + cusip + '    No corresponding time series file!'
        return {"state":0}
    else:
        data = pd.read_csv(('crsp/' + cusip + '.csv'),
                names = ['CUSIP', 'PERMNO', 'PERMCO', 'ISSUNO', 'HEXCD', 'HSICCD',
                        'DATE', 'BIDLO', 'ASKHI', 'PRC', 'VOL', 'RET',
                        'BID', 'ASK', 'SHROUT', 'CFACPR', 'CFACSHR',
                        'OPENPRC', 'NUMTRD', 'RETX'], parse_dates = ['DATE'],
                        index_col = 'DATE')
        ret = data['RET']
        ret = ret[(ret != 'C') & (ret != 'B')]
        ret = ret.astype(float)
        return {"state":1, "data":ret} 
   
  


def getSingleCAR(date, cusip,cik,sp):
    '''
    get the CAR for window {0}, {-1, +1}, {-2,+2}, {-3,+3}, {-5,+5}
    
    '''
    CARFilePath = 'CAR_Results.csv'
    if not os.path.exists(CARFilePath):
        with open(CARFilePath, 'w') as carFile:
            carFile.write('CUSIP,CIK,Filing Date t,t-5 Date,t-5 Return,' + 
                        't-4 Date,t-4 Return,t-3 Date,t-3 Return,' + 
                        't-2 Date,t-2 Return,t-1 Date,t-1 Return,' + 
                        't Date,t Return,t+1 Date,t+1 Return,t+2 Date,t+2 Return,' + 
                        't+3 Date,t+3 Return,t+4 Date,t+4 Return,' +
                        't+5 Date,t+5 Return,window{0} CAR,window{-1 +1} CAR,' + 
                        'window{-2 +2} CAR,window{-3 +3} CAR,window{-5 +5} CAR}\n')
    
    query = loadStockReturn(cusip)
    if query['state'] == 0:
        return None
    data = query['data']
    
    #Check whether there are enough data points for regression
    #i.e the number of data points within -345 to -91 days is greater than 100
    #ipdb.set_trace()

    
    dt_date = parse(date)
    dt_regBegin = dt_date - dt.timedelta(days = 345)
    dt_regEnd = dt_date - dt.timedelta(days = 91)
    
    regBegin = dt_regBegin.strftime('%Y%m%d')
    regEnd = dt_regEnd.strftime('%Y%m%d')
    regData = data.ix[regBegin:regEnd]
    if len(regData) < 100:
        return None

    #conduct the regression
    spExcerpt = sp.ix[regData.index]
    regX = spExcerpt['sprtrn'].values
    regX = np.array([regX, np.ones(len(regX))])
    regY = regData.values
    w = np.linalg.lstsq(regX.T,regY)[0]
    beta = w[0]
    alpha = w[1]
     
    CAR = np.zeros((11))
    #Only consider the situation where filing date is also a trading date
    if date in data.index:
        index0 = data.index.get_loc(date)
        #check the upper and lower window is within the data range
        if (index0 >=5) and (index0 <= (len(data) - 6)):
            with open(CARFilePath, 'a') as f:
                f.write(cusip + ',' + cik + ',' + date + ',')
                for windowIndex in range(index0 - 5, index0 + 6):
                    windowDate = data.index[windowIndex]
                    f.write(windowDate.strftime('%Y%m%d') + ',')
                    r_real = float(data.ix[windowIndex])
                    r_market = float(sp.ix[windowDate]['sprtrn'])
                    r_pred = alpha + beta * r_market
                    CAR[windowIndex - index0] = r_real - r_pred
                    f.write(str(r_real - r_pred) + ',')
                #window 0     
                f.write(str(CAR[5]) + ',')
                #window -1 to +1
                f.write(str(np.sum(CAR[4:7])) + ',')
                #window - 2 to +2
                f.write(str(np.sum(CAR[3:8])) + ',')
                #window -3 to +3
                f.write(str(np.sum(CAR[2:9])) + ',')
                #window -5 to +5
                f.write(str(np.sum(CAR[0:11])) + '\n')


def generateCARTable(start = 0):
    '''
    Generate CAR file for each entry in the master file
    '''
    
    masterFile = pd.read_csv('Master.idx', header = None,
                            names = ['DATE', 'CIK', 'CUSIP'], dtype ={'DATE':str, 'CIK':str, 'CUSIP':str})
    
    CARFilePath = 'CAR_Results.csv'

    sp = loadSPReturn() 
    for i in range(start, len(masterFile)):
        #if count == 21:
        #    ipdb.set_trace()
        print i 
        row = masterFile.ix[i]
        date = row['DATE']
        cik = row['CIK']
        cusip = row['CUSIP']
        
        getSingleCAR(date, cusip, cik, sp)
          

