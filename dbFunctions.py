import os
import mysql.connector

def GetConnection():
    dbConnection = mysql.connector.connect(
      host=os.environ.get("sqlhost"),
      user=os.environ.get("sqluser"),
      password=os.environ.get("sqlpass"),
      database="train_data"
    )
    dbCursor = dbConnection.cursor()
    return dbConnection,dbCursor