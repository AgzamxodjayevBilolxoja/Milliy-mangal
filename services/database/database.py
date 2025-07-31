import sqlite3

class Database:
    def __init__(self):
        self.__conn = sqlite3.connect('db.sqlite3')
        self.__cur = self.__conn.cursor()
    
    def execute(self, sql: str, parametrs: tuple=None, commit: bool=False, fetchall: bool=False, fetchone: bool=False):
        if parametrs:
            data = self.__cur.execute(sql, parametrs)
        else:
            data = self.__cur.execute(sql)
        
        if commit:
            self.__conn.commit()
        elif fetchall:
            return data.fetchall()
        elif fetchone:
            return data.fetchone()