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
        vals = (userID, )
        sqlQuery = 'select * from userData where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()

        if dataType == "userBalance":
            return result[1]
        elif dataType == "colorPref":
            return result[2]
        elif dataType == "sortPref":
            return result[3]

    @classmethod
    def updateUserBalance(cls, userID: str, balance: int):
        vals = (balance, userID)
        sqlQuery = 'update userData set userBalance = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
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
        dataTuple = (userID, 10000, "#00ff00", 'd')
        DBCursor.execute(query, dataTuple)
        botDB.commit()
