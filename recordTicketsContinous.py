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

tryCounter = 0

targetDate = "25.12.2022"
startLocation = "Eskişehir"
terminationLocation = "İstanbul(Söğütlü Ç.)"

currentStartLocation = "Eskişehir"
currentTerminationLocation = "İstanbul(Söğütlü Ç.)"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome('C:/Users/Sertan/Downloads/chromedriver_win32/chromedriver',chrome_options=options)

class TrainTrip:
    hour = ""
    economyCount = 0
    businessCount = 0
    tripDate : datetime = None
    fetchDate : datetime = None
    tripDirection = "" 

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
    if len(trainTrips)>0:
        print("Trains available!")
    for h in trainTrips:
        # print(h.hour)
        print(h.tripDate)
        print("Economy count "+str(h.economyCount))
        print("Business count "+str(h.businessCount))

def RecordTrips():
    for t in trainTrips:
        # print(h.hour)
        print("Trip Date"+str(t.tripDate))
        print("Economy count "+str(t.economyCount))
        print("Business count "+str(t.businessCount))
        print("Fetch Date"+str(t.tripDate))
        print("Trip Direciton"+str(t.tripDirection))
    

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
    currentTime = datetime.now()
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
            # time.sleep(3+random.randint(-2, 2))
            time.sleep(1)

    # time.sleep(1800) 
    time.sleep(1) 