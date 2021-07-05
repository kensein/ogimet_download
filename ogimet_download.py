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

def main(argv):
    beginyear = ''
    endyear = ''
    try:
        opts, args = getopt.getopt(argv, "hb:e:", ["begin=", "end="])
    except getopt.GetoptError:
        print('error: see ogimet_download.py -h')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('ogimet_download.py -b <beginyear> -e <endyear>')
            sys.exit()
        elif opt in ("-b", "--begin"):
            beginyear = arg
        elif opt in ("-e", "--end"):
            endyear = arg

    # time_format = '2019122903' # example time format
    save_path = './' # directory at your own pc
    json_stat_path = './' # directory at your own pc
    begin = beginyear + '010100'
    end = endyear + '123123'
    url = 'https://www.ogimet.com/cgi-bin/getsynop?begin=' + begin + '00&end=' + end + '59&state=Indonesia'
    http = urllib3.PoolManager()
    res = http.request('GET',url)
    data = res.data.decode('utf-8').splitlines()
    stasiun = open(json_stat_path + 'stasiun.json')
    stasiunj = json.load(stasiun)
    cols = ['wmo_id', 'yy', 'mm', 'dd', 'hh', 'date', 'lat','lon', 'T_code', 'Td_code', 'Press_code', 'T','Td','Press', 'LCL', 'CCL']
    syndata = []
    for line in data:
        line = line.split(' ')
        if not line[3] == 'NIL=':
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
                for i in line[0:10]:
                    if i[0] == "1":
                        code_T = i
                        T = int(code_T[-3:])/10
            except:
                T = float('NaN')
            try:
                for i in line[0:10]:
                    if i[0] == "2":
                        code_Td = i
                        Td = int(code_Td[-3:])/10
            except:
                Td = float('NaN')
            try:
                for i in line[0:10]:
                    if i[0] == "4":
                        code_press = i
                        press = 1000+(int(code_press[-4:])/10)
            except:
                press = float('NaN')
            lcl = 125*(T-Td)
            ccl = 212.7*(T-Td)
            syndata.append([wmo, YY, MM, DD, HH, date, lat, lon, code_T, code_Td, code_press, T, Td, press, lcl, ccl])
    syndf = pd.DataFrame(syndata,columns=cols)
    # syndf = syndf[syndf['wmo'].str.contains("96935")] # uncomment this line if you want to choose specific wmo_id
    file_name = save_path + 'indonesian_synop_' + str(beginyear) + "_" + str(endyear) + ".csv"
    syndf.to_csv(file_name)

if __name__ == "__main__":
    main(sys.argv[1:])