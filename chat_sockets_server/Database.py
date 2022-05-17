import mysql.connector

class Database():
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="db_chat_app"
        )
        self.cursor = self.db.cursor()
    
    def runCreateQuery(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()
    
    def runReadQuery(self, sql):
        self.cursor.execute(sql)
        self.db.close()
    
    def runVerifyQuery(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]