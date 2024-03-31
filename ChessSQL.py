
from re import T
import sqlite3
import os
from sqlite3 import Connection, Error


import json

class SQLite():
    def __init__(self, path_to_db : str) -> None:
        self.path_to_db = path_to_db
        self.conn = None
        self.db = self.create()
        pass

    def create(self) -> Connection: 
        
        database = f"{os.getcwd()}" + "\\" + self.path_to_db

        try:
            conn = sqlite3.connect(database)
            print(sqlite3.version)
        except Error as e:
            print(e)
            return None
        
        if conn is not None:
            sql_create_games_table = """ CREATE TABLE IF NOT EXISTS games (
                                            id integer PRIMARY KEY AUTOINCREMENT,
                                            channel_id integer NOT NULL,
                                            user_1 text NOT NULL,
                                            user_2 text NOT NULL,
                                            color_playing text NOT NULL,
                                            winner text NOT NULL
                                            
                                        ); """
            
            sql_create_echequiers_table = """ CREATE TABLE IF NOT EXISTS echequiers (
                                            id integer PRIMARY KEY,
                                            channel_id integer NOT NULL,
                                            pieces text NOT NULL
                                        ); """

            try:
                c = conn.cursor()
                c.execute(sql_create_games_table)
                c.execute(sql_create_echequiers_table)
            except Error as e:
                print(e)
        else:
            print("Error! cannot create the database connection.")
        self.conn = conn
        return conn
    
    def add_game(self, data : T) -> None:
        dict_data = data.todict()


        dict_data['user_1'] = json.dumps(dict_data['user_1'])
        dict_data['user_2'] = json.dumps(dict_data['user_2'])


        sql = f''' INSERT INTO {"games"} ({",".join(dict_data.keys())})
              VALUES({','.join(['?'] * len(dict_data.keys()) )}) '''

        cur = self.conn.cursor()
        cur.execute(sql, tuple(dict_data.values()))
        self.conn.commit()

    def add_echequier(self, data : T) -> None:
        dict_data = data.todict()

        dict_data['pieces'] = json.dumps(dict_data['pieces'])

        sql = f''' INSERT INTO {"echequiers"} ({",".join(dict_data.keys())})
              VALUES({','.join(['?'] * len(dict_data.keys()) )}) '''

        cur = self.conn.cursor()
        cur.execute(sql, tuple(dict_data.values()))
        self.conn.commit()

    
    def find_by(self, dict_data: dict, table: str) -> list:
        where = ""
        if dict_data:
            p = []
            for key in dict_data.keys():
                p.append(f"{key} = ?")
            where = f"WHERE {','.join(p)}"

        sql = f"SELECT * FROM {table} {where}"
        cur = self.conn.cursor()
        cur.execute(sql, tuple(dict_data.values()))

        rows = cur.fetchall()
        cur.close()
        return rows

    def list_all(self, table: str) -> list:
            return self.find_by({}, table)
    
    def update_by_id(self, dict_data, table, id, remove_id_from_dict=True):
        
        if table == "games":
            dict_data['user_1'] = json.dumps(dict_data['user_1'])
            dict_data['user_2'] = json.dumps(dict_data['user_2'])

        elif table == "echequiers":
            dict_data['pieces'] = json.dumps(dict_data['pieces'])

        if remove_id_from_dict:
            del(dict_data['id'])
        p = []
        for key in dict_data.keys():
            p.append(f"{key} = ?")
        set_params = ','.join(p)

        sql = f''' UPDATE {table}
                SET {set_params}
                WHERE id = {id}'''
        
        cur = self.conn.cursor()
        cur.execute(sql, tuple(dict_data.values()))
        self.conn.commit()

    def get_next_id(self):
        cur = self.conn.cursor()
        cur.execute("SELECT MAX(id) FROM games")
        last_id = cur.fetchone()[0]
        self.conn.commit()

        return last_id+1 if last_id is not None else 1
