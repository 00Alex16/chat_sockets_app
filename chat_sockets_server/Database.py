import mysql.connector

class Database():
    def __init__(self):
        self.db = mysql.connector.connect(
            # Datos para conectarse a la BD
            host="db4free.net",
            user="jalex_bd",
            password="db_chat_app_pass",
            database="db_chat_app_sock"
        )
        self.cursor = self.db.cursor()
    
    # Se ejecuta sql que almacena info en la BD
    def runCreateQuery(self, sql):
        self.cursor.execute(sql)
        self.db.commit()
        self.db.close()
    
    def runReadQuery(self, sql):
        self.cursor.execute(sql)
        self.db.close()
    
    # Se ejecuta sql que retorna info de la BD
    def runVerifyQuery(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]