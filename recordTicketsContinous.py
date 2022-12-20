from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
import sys
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()
chrome_driver_adress = os.environ.get("chromedadress")

tryCounter = 0

targetDate = "25.12.2022"
startLocation = "Eskişehir"
terminationLocation = "İstanbul(Söğütlü Ç.)"

currentStartLocation = "Eskişehir"
currentTerminationLocation = "İstanbul(Söğütlü Ç.)"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--headless')

driver = webdriver.Chrome(chrome_driver_adress,chrome_options=options)

dbConnection = mysql.connector.connect(
  host=os.environ.get("sqlhost"),
  user=os.environ.get("sqluser"),
  password=os.environ.get("sqlpass"),
  database="train_data"
)

cursor= dbConnection.cursor()
addQuery = "INSERT INTO trips (trip_date, data_date, trip_direction, empty_economy, empty_business) VALUES (%s, %s, %s, %s,%s)"

class TrainTrip:
    hour = ""
    economyCount = 0
    businessCount = 0
    tripDate : datetime = None
    fetchDate : datetime = None
    tripDirection = ""

    def Add2Table(self,cursor):
        #  query = "INSERT INTO trips (trip_date, data_date, trip_direction, empty_economy, empty_business) VALUES ({0}, {1}, {2}, {3},{4});".format(self.tripDate,self.fetchDate,self.tripDirection,self.economyCount,self.businessCount)
         query = "INSERT INTO trips (trip_date, data_date, trip_direction, empty_economy, empty_business) VALUES (%s, %s, %s, %s,%s)"
         values = (self.tripDate,self.fetchDate,self.tripDirection,self.economyCount,self.businessCount)
         cursor.execute(query,values)
    def GetValuesTupple(self):
        return (self.tripDate,self.fetchDate,self.tripDirection,self.economyCount,self.businessCount)

def ConvertToIntHour(stringHour):
    jHour = stringHour.replace(":", "")
    return int(jHour)

hourStart = "05:00"
hourStartInt = ConvertToIntHour(hourStart)
hourEnd = "20:00"
hourEndInt = ConvertToIntHour(hourEnd)

trainTrips = []

lastDate = date.today()

def ClickForResults(date2check : date):
    global tryCounter
    global lastDate
    if(tryCounter>2):
        return 
    
    driver.get('https://ebilet.tcddtasimacilik.gov.tr/view/eybis/tnmGenel/tcddWebContent.jsf')

    lastDate = date2check
    targetDate = date2check.strftime("%d.%m.%Y")
    print(targetDate)

    nereden = driver.find_element(By.ID,"nereden")
    nereye = driver.find_element(By.ID,"nereye")
    date = driver.find_element(By.ID,"trCalGid_input")
    submitB = driver.find_element(By.ID,"btnSeferSorgula")
    #For get results
    time.sleep(0.3)
    nereden.clear()
    nereden.send_keys(currentStartLocation)
    time.sleep(0.3)
    nereye.clear()
    nereye.send_keys(currentTerminationLocation)
    time.sleep(0.3)
    date.clear()
    date.send_keys(targetDate)
    time.sleep(0.3)
    driver.find_element(By.XPATH,"//body").click()
    time.sleep(0.3)
    submitB.click()

def PostResults(day : date, queryTime : datetime):
    global tryCounter
    #After get results
    time.sleep(3)
    if(tryCounter>2):
        return 
    try:
        element = WebDriverWait(driver, 2).until(
            # EC.presence_of_element_located((By.ID, "mainTabView:gidisSeferTablosu:j_idt78"))
            EC.visibility_of_element_located((By.ID, "mainTabView:gidisSeferTablosu:j_idt78"))
        )
    except:
        print("Exception")
        tryCounter += 1
        ClickForResults(lastDate)
        PostResults(day,queryTime)
        return
    finally:
        print("")
    print("Potato")
    rows = driver.find_elements(By.XPATH,'//tr[@role="row"]')
    for row in rows:

        hour = row.find_element(By.TAG_NAME,"span")

        hourText = hour.text
        if(hourText=="Çıkış"):
            continue

        justHour = hourText.replace(":", "")

        if justHour=='':
            continue
        
        intHour = int(justHour)

        if intHour>hourEndInt:
            continue
        elif intHour<hourStartInt:
            continue

        trainTrip = TrainTrip()
        trainTrip.fetchDate = queryTime
        trainTrip.hour = hourText
       
        tripTime = datetime.strptime(hourText, "%H:%M").time()
        tripDateTime = datetime.combine(day, tripTime)
        trainTrip.tripDate = tripDateTime

        # print(hourText)

        hiddenDiv=None
        try:
            hiddenDiv = row.find_element(By.XPATH,".//div[@class='ui-helper-hidden']")
        except:
            print("An exception occurred")

        if(hiddenDiv==None):
            continue

        hiddenDiv2 = row.find_element(By.XPATH,".//div[@class='ui-helper-hidden']")
        hiddenDivHTML = (hiddenDiv2.get_attribute('innerHTML'))

        hiddenSoup = BeautifulSoup(hiddenDivHTML,features="lxml")
        soupOptions = hiddenSoup.find_all("option")

        typeCounter=0
        for sop in soupOptions:
            sopTxt = sop.text
            len(sopTxt)
            countTxt=""
            pastBracked = False
            for i in range(len(sopTxt)-1,0,-1):
                character = sopTxt[i]
                if(character==')'):
                    pastBracked=True
                    continue
                
                if(character=='('):
                    break
                countTxt = character + countTxt

            availableCount = int(countTxt)
            trainType = "Economy"
            if typeCounter==1:
                trainType = "Business"
                trainTrip.businessCount = int(countTxt)
            else:
                trainTrip.economyCount = int(countTxt)
            # print("Available count in "+trainType+" "+countTxt)
            typeCounter+=1

        # if trainHour.economyCount>2 or trainHour.businessCount>0:
        trainTrips.append(trainTrip)    

searching = True

def PrintTrips():
    for t in trainTrips:
        # print(h.hour)
        print("Trip Date"+str(t.tripDate))
        print("Economy count "+str(t.economyCount))
        print("Business count "+str(t.businessCount))
        print("Fetch Date"+str(t.tripDate))
        print("Trip Direciton"+str(t.tripDirection))

def RecordTrips():
    valueTupples = []
    for t in trainTrips:
        valueTupples.append(t.GetValuesTupple())
        # t.Add2Table(cursor)
    if(len(valueTupples)<1):
        return
    cursor.executemany(addQuery, valueTupples)
    
def SetCurrentDirection(directionIndex : int):
    global currentStartLocation
    global currentTerminationLocation
    if (directionIndex==0):
        currentStartLocation = startLocation
        currentTerminationLocation = terminationLocation
    else:
        currentStartLocation = terminationLocation
        currentTerminationLocation = startLocation

directionList = ["Esk-Ist","Ist-Esk"]

def AddDirection(directionIndex):

     for t in trainTrips:
        t.tripDirection = directionList[directionIndex]

while(searching):
    today = date.today()
    activeDay=today
    currentTime = datetime.now().replace(microsecond=0)
    print(currentTime)
    for dateIndex in range(30):
        for directionIndex in range(2):
            SetCurrentDirection(directionIndex)
            tryCounter = 0
            activeDay = today+timedelta(days=dateIndex)
            trainTrips.clear()
            ClickForResults(activeDay)
            PostResults(activeDay,currentTime)
            AddDirection(directionIndex)
            # PrintTrips()
            RecordTrips()
            time.sleep(1)

    time.sleep(1800) #Scrape each 30 minutes
    # time.sleep(1) 
