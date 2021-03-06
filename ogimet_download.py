# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 16:04:46 2021

@author: KenSein
copyright: Center for Research and Development
Contact: mohamad.nurrahmat@bmkg.go.id

Ogimet Historical Data Series
"""

import urllib3 
import json
import pandas as pd
from datetime import datetime
import sys, getopt
import re

def main(argv):
    begindate = ''
    enddate = ''
    try:
        opts, args = getopt.getopt(argv, "hb:e:", ["begin=", "end="])
    except getopt.GetoptError:
        print('error: see ogimet_download.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('ogimet_download.py -b <yyyymmdd> -e <yyyymmdd>')
            sys.exit()
        elif opt in ("-b", "--begin"):
            begindate = arg
        elif opt in ("-e", "--end"):
            enddate = arg

    # time_format = '20191229' # example time format
    save_path = './' # directory at your own pc
    json_stat_path = './' # directory at your own pc
    begin = begindate
    end = enddate
    url = 'https://www.ogimet.com/cgi-bin/getsynop?begin=' + begin + '0000&end=' + end + '2359&state=Indonesia'
    http = urllib3.PoolManager()
    res = http.request('GET',url)
    data = res.data.decode('utf-8').splitlines()
    stasiun = open(json_stat_path + 'stasiun.json')
    stasiunj = json.load(stasiun)
    cols = ['wmo_id', 'yy', 'mm', 'dd', 'hh', 'date', 'lat','lon', 'T_code', 'Td_code', 'Press_code', 'T','Td','Press', 'LCL', 'CCL']
    syndata = []
    code_T = float('NaN')
    code_Td = float('NaN')
    code_press = float('NaN')
    T = float('NaN')
    Td = float('NaN')
    press = float('NaN')
    for line in data:
        line = line.split(' ')
        if not line[1][-1:] == '=' or line[2][-1:] == '=' or line[3] == 'NIL=':
            col1 = line[0].split(' ')[0].split(',')
            wmo = col1[0]
            YY = col1[1]
            MM = col1[2]
            DD = col1[3]
            HH = col1[4]
            date = str(YY + MM + DD + HH)
            date = datetime.strptime(date, '%Y%m%d%H')
            lat = stasiunj[wmo]['lat']
            lon = stasiunj[wmo]['lon']
            try:
                for i in line[3:10]:
                    if bool(re.match("^10...", i[0:5])) == True:
                        code_T = i
                        T = int(code_T[-3:])/10
            except:
                pass
            try:
                for i in line[3:10]:
                    if bool(re.match("^20...", i[0:5])) == True:
                        code_Td = i
                        Td = int(code_Td[-3:])/10
            except:
                pass
            try:
                for i in line[4:10]:
                    if bool(re.match("^4....", i[0:5])) == True:
                        code_press = i
                        press = 1000+(int(code_press[-4:])/10)
            except:
                pass
            lcl = 125*(T-Td)
            ccl = 212.7*(T-Td)
            syndata.append([wmo, YY, MM, DD, HH, date, lat, lon, code_T, code_Td, code_press, T, Td, press, lcl, ccl])
    syndf = pd.DataFrame(syndata,columns=cols)
    # syndf = syndf[syndf['wmo'].str.contains("96935")] # uncomment this line if you want to choose specific wmo_id
    file_name = save_path + 'indonesian_synop_' + str(begindate) + "_" + str(enddate) + ".csv"
    syndf.to_csv(file_name, index = False)

if __name__ == "__main__":
    main(sys.argv[1:])
