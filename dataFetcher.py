import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

# def getDBConnection():
#     _dbConnection = mysql.connector.connect(
#         host=os.environ.get("sqlhost"),
#         user=os.environ.get("sqluser"),
#         password=os.environ.get("sqlpass"),
#         database="train_data"
#     )
#     return _dbConnection

dbConnection = mysql.connector.connect(
  host=os.environ.get("sqlhost"),
  user=os.environ.get("sqluser"),
  password=os.environ.get("sqlpass"),
  database="train_data"
)
cursor= dbConnection.cursor()

def GetTripsBetweenDataDates(dataDateFrom,dataDateTo):
    query = f'select * from trips where (data_date>="{dataDateFrom}" and data_date<="{dataDateTo}");'
    cursor.execute(query)
    tripsBetween = cursor.fetchall()
    return tripsBetween

def GetTripsBetweenTripDates(tripDateFrom,tripDateTo):
    query = f'select * from trips where (trip_date>="{tripDateFrom}" and trip_date<="{tripDateTo}");'
    cursor.execute(query)
    tripsBetween = cursor.fetchall()
    return tripsBetween

def GetTripsBetweenTripDateAndDataDate(tripDateInterval,dataDateInterval):
    query = f'select * from trips where (trip_date>="{tripDateInterval[0]}" and trip_date<="{tripDateInterval[1]}" and \
        data_date>="{dataDateInterval[0]}" and data_date<="{dataDateInterval[1]}");'
    cursor.execute(query)
    tripsBetween = cursor.fetchall()
    return tripsBetween

def GetEmptyEconomyBetweenTripDateAndDataDate(tripDateInterval,dataDateInterval):
    query = f'select trip_date,data_date,empty_economy from trips where (trip_date>="{tripDateInterval[0]}" and trip_date<="{tripDateInterval[1]}" and \
        data_date>="{dataDateInterval[0]}" and data_date<="{dataDateInterval[1]}");'
    cursor.execute(query)
    tripsBetween = cursor.fetchall()
    return tripsBetween

_trips = GetTripsBetweenTripDateAndDataDate(["2023-01-11 19:10:00","2023-01-11 22:10:00"],["2023-01-9 19:10:00","2023-01-11 22:10:00"])
print(_trips)
    # addQuery = "INSERT INTO trips (trip_date, data_date, trip_direction, empty_economy, empty_business) VALUES (%s, %s, %s, %s,%s)"