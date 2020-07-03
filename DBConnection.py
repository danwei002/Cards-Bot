import mysql.connector
import json

with open('credentials.json') as cred:
    credentials = json.load(cred)

botDB = mysql.connector.connect(host=credentials["host"], user=credentials["username"],
                                password=credentials["password"], database=credentials["database"])
DBCursor = botDB.cursor()

class DBConnection:
    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        DBCursor.execute("select " + dataType + " from userData where userID = " + userID)
        result = DBCursor.fetchone()
        return result[0]

    @classmethod
    def updateUserData(cls, dataType: str, userID: str, updatedValue):
        if dataType == "userBalance":
            DBCursor.execute("update userData set " + dataType + " = " + str(updatedValue) + " where userID = " + userID)
            botDB.commit()
        else:
            DBCursor.execute("update userData set " + dataType + " = '" + str(updatedValue) + "' where userID = " + userID)
            botDB.commit()


    @classmethod
    def checkUserInDB(cls, userID: str):
        DBCursor.execute("select * from userData where userID = " + userID)
        result = DBCursor.fetchall()
        return len(result) != 0

    @classmethod
    def addUserToDB(cls, userID: str):
        query = """INSERT INTO userData (userID, userBalance, colorPref, sortPref) 
                VALUES (%s, %s, %s, %s) """
        dataTuple = (userID, 10000, "#00ff00", 'd', "default")
        DBCursor.execute(query, dataTuple)
        botDB.commit()
