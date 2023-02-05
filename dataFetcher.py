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
    query = f'select * from trips where (data_date>"{dataDateFrom}" and data_date<"{dataDateTo}");'
    cursor.execute(query)
    tripsBetween = cursor.fetchall()
    return tripsBetween

_trips = GetTripsBetweenDataDates("2023-01-11 19:10:00","2023-02-15 19:10:00")
print(_trips)
    # addQuery = "INSERT INTO trips (trip_date, data_date, trip_direction, empty_economy, empty_business) VALUES (%s, %s, %s, %s,%s)"