# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 22:52:57 2018

@author: Lili
"""
# tidal_sample.xlsx

import Tkinter
from Tkinter import *
import tkMessageBox 
import pandas as pd
import requests
import urllib2

variable = {}
selectedData={}
dict1={}

#Write data into Excel sheet
def WriteData(df1,Wtname):
    writer=pd.ExcelWriter(Wtname) 
    df1.to_excel(writer,'Sheet1')
    writer.save()
    
#Save data for user into Excel sheet 
def SaveDataForUser(df1):
    #change the WaterLevel data  to numeric
    df1['WaterLevel']=df1['WaterLevel'].apply(pd.to_numeric, errors='coerce')
    df1['DatumRefDepth']=df1['DatumRefDepth'].apply(pd.to_numeric, errors='coerce')
    #change the format of WaterLevel and DatumRefDepth 
    format = lambda k: '%.1f' % k
    df1['WaterLevel']=df1['WaterLevel'].map(format)
    df1['DatumRefDepth']=df1['DatumRefDepth'].map(format)
    #replace the . in the sheet to , 
    df1['DatumRefDepth']=df1['DatumRefDepth'].str.replace('.',',')
    df1['WaterLevel']=df1['WaterLevel'].str.replace('.',',')
    #move WaterLevel and DatumRefDepth next depth   
    wl=df1.pop('WaterLevel')
    df1.insert(6,'WaterLevel',wl)    
    dd=df1.pop('DatumRefDepth')
    df1.insert(7,'DatumRefDepth',dd)
    # write data    
    WriteData(df1,'DataForUser.xlsx')

#Save data to excel file   
def Savedata(df1,waterlevel):
    
    z = df1['depth'].str.replace(',','.').apply(pd.to_numeric, errors='coerce')
    #insert Waterlevel data in the spread Excel sheet
    df1['WaterLevel']=pd.Series(waterlevel)
    #Covert water level format
    s=df1['WaterLevel'].apply(pd.to_numeric, errors='coerce')
    #generate datum referrenced depth
    datumrefdepth=z.sub(s)# calculate datum referenced depth    
    df1['DatumRefDepth']=pd.Series(datumrefdepth)    
    WriteData(df1,'DataForMe.xlsx')    
    SaveDataForUser(df1)
    
#Get the waterlevel data from Kartverket
def Getdepth(url) :
    
    #request waterlevel data from Kartverket
    data = urllib2.urlopen(url)
    
    #if proxy is needed to open the url, then following code is needed:    
    #proxy = urllib2.ProxyHandler({'http': '127.0.0.1'})
    #opener = urllib2.build_opener(proxy)
    #urllib2.install_opener(opener)
    #data = urllib2.urlopen(url)
    
    # get the water level data
    level = []    
    for line in data:
     if("#" in line):
         continue
     elif('version="1.0"'  in line):
         level.append('error')
         break
     else:
        a=line.split()
        level.append(a[1])         
    return level
 
# generate  request used time 
def Generatetime(timefrom3):
    
    timefrom_spli = timefrom3.split(':')        
    timefrom_min = int(timefrom_spli[1])
    timefrom_hour = timefrom_spli[0] 
    #generate timefrom adn timeto
    if timefrom_min in range(00,10):
        timefrom_min1 = "00"
        timeto_min1= "10"
        timeto_hour=timefrom_hour
    elif timefrom_min in range(10,20):
        timefrom_min1="10"
        timeto_min1="20"
        timeto_hour=timefrom_hour
    elif timefrom_min in range(20,30):
        timefrom_min1="20"
        timeto_min1="30"
        timeto_hour=timefrom_hour
    elif timefrom_min in range(30,40):
        timefrom_min1="30"
        timeto_min1="40"
        timeto_hour=timefrom_hour
    elif timefrom_min in range(40,50):
        timefrom_min1="40"
        timeto_min1="50"
        timeto_hour=timefrom_hour
    else:
        timefrom_min1="50"
        timeto_min1="00"
        timeto_hour=int(timefrom_hour)+1
        timeto_hour="%02d" % timeto_hour          
    timef=str(timefrom_hour)+":"+timefrom_min1
    timet=str(timeto_hour)+":"+timeto_min1
    #get the difference of  minutes 
    timed = float(timefrom_min1)- float(timefrom_min)
    return timef, timet, timed
 
#calculat datum referrenced water level 
def DataGenerate(filename): 
    
    df1=pd.DataFrame(xls)

    y=pd.to_datetime(df1['Date'],errors='coerce')
    #define waterlevel and depth
    waterlevel=[] 
    datumrefdepth=[]
    
    #store flag for date, latitude, longitude, time whether they are true or false in the dataframe
    date_null=pd.isnull(df1['Date'])
    date_null2=pd.notnull(df1['Date'])
    lati_null=pd.isnull(df1['GPS Latitude'])
    longi_null=pd.isnull(df1['GPS Longitude'])
    time_null=pd.isnull(df1['Time'])
    #get water level data from Kartverket)
    for n in range (0,len(df1)):
        #define an array for storing data from url API web for each observations
        #level=[]
        #latitude,longitude, date,time value
        Latitude=df1.iloc[n,3]
        Longitude=df1.iloc[n,4]
        depth=df1.iloc[n,5]
        datefromend=y.iloc[n].date()
        timefrom3=df1.iloc[n,1]
        #check date, latitude, longitude, time whether they are nan or not in the dataframe
        if (time_null[n]==True or date_null[n]==True or lati_null[n]==True or longi_null[n]==True):               
            waterlevel.append('NaN')
            #tkMessageBox.showinfo(title='warning', message = 'NaN value in pandas dataframe')
            print 'NaN value in pandas dataframe' 
        elif (timefrom3=='<Null>' or datefromend=='<Null>' or Latitude=='<Null>' or Longitude=='<Null>'): 
            waterlevel.append('NaN')
            #tkMessageBox.showinfo(title='warning', message = 'No  value in line ')
            print 'NULL value in pandas dataframe'
        else:
            timefrom2, timeto, timed1 = Generatetime(timefrom3)            
            
            #to make the timefrom and timeto format as '2014-02-14T14:30'
            dt2from=str(datefromend)+'T'+str(timefrom2)
            dt2to=str(datefromend)+'T'+str(timeto) 
            #request water level data from Kartverket
            
            interval=dict1['interval']
            language=dict1['language']
            datatype=dict1['datatype']
            filetype=dict1['filetype']
            place=dict1['place']
            
            
            requesturl="http://api.sehavniva.no/tideapi.php?tide_request=locationdata&lat={}&lon={}&datatype=ALL&file=txt&lang=nl&place=Gol&dst=1&refcode=CD&fromtime={}&totime={}&interval=10".format(Latitude, Longitude, dt2from, dt2to)

             #download the chunk of the data 
             #import requests
             #http_proxy  = "http://www-proxy.nov.no:140"
             #https_proxy = "http://www-proxy.nov.no:140"
             #proxyDict = { 
                 # "http"  : http_proxy, 
                 # "https" : https_proxy 
             # }
             #r = requests.get(url, stream=True,proxies=proxyDict)
             #with open("f_{}.txt".format(depth), 'wb',) as f:
                 #for chunk in r.iter_content(): 
                     #if chunk:# filter out keep-alive new chunks
                         #f.write(chunk)          
           
            waterlevelsamp = Getdepth(requesturl)                
            # calculate water level 
            if (waterlevelsamp[0]!='error'):
                slevel= float(waterlevelsamp[0]) + (float(waterlevelsamp[1])-float(waterlevelsamp[0]))*(timed1)/10
            #change cm to m 
                slevel=slevel/100
                waterlevel.append(slevel)
            else:
                slevel='error'
                waterlevel.append(slevel)  
                   
    Savedata(df1,waterlevel)

#read Excel file
def ReadExcel(filename):
    
    global xls
    #read Excel sheet
    xls = pd.read_excel(filename)
    if (pd.DataFrame(xls).empty):
        tkMessageBox.showinfo(title='warning', message = 'The given excel sheet is empty!')
    else:
        DataGenerate(xls)

def dropbox(OPTIONS,master,OPTIONSName):
    
    global variable
    i=10
    l1 = Label(master, text=OPTIONSName)
    l1.pack()
    
    variable[OPTIONSName] = StringVar(master)
    variable[OPTIONSName].set(OPTIONS[0]) # default value
    
    
    w = OptionMenu(master, variable[OPTIONSName], *OPTIONS)
    w.pack()
    
def fileter(master):
    
    l3 = Label(master, text="please select suitable parameters :")
    l3.pack() 
    
    selectedData={'datatype':[ "TAB", "PRE", "OBS", "ALL"], 
                  'interval': ["10","20"], 
                  'language':[ "nb_Bokmal", "nn_Nynorsk",  "en_English", "de_Deutsch",  "en_Nederlands",  "de_Davvisamegiella"],
                  'filetype': ["txt","pdf", "xml" ]}
    #print selectedData.items()
    #selectedITems=selectedData.keys()   
   
    for dt,dv in selectedData.items():        
        dropbox(dv,master,dt)
        
# Calculate datum referrenced depth for input file and write result 
def on_click():
    
    global dict1
    print({k:v.get() for k,v in variable.items()})
    dict1={k:v.get() for k,v in variable.items()}
    #print dict1.keys()
    #print dict1['int(erval']
    filenameinput = dict1['inputfile']    
    #print("xls name：%s " %(filenameinput))
    ReadExcel(filenameinput) 
    tkMessageBox.showinfo(title='Done', message = 'Results output to DataForUser.xlsx and DataForMe.xlsx ')
    
def Opendialogue():
    
    global variable
    master=Tk()
    master.title("Datum Referrenced Water Level Generator")
    master.geometry('600x450')
    
    
    l1 = Label(master, text="Input your directory and  xls file name here:")
    l1.pack()
    
    variable['inputfile'] = StringVar()
    xls = Entry(master,textvariable = variable['inputfile'])
    xls.pack()
    filepn=variable['inputfile'].get()
    
    l2 = Label(master, text="Input the city or place to get waterlevel data:")
    l2.pack()
    
    variable['place'] = StringVar()
    xls = Entry(master,textvariable = variable['place'])
    xls.pack()
    
    fileter(master) 
    
    button = Button(master, text="Run the Script", command = on_click)
    button.pack(side=BOTTOM)
    
    mainloop()

Opendialogue()