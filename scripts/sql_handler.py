import sqlite3
import re

class sql_handler():

    def __init__(self):
        self.delimiter = r'␞'
    
    def dict_to_db(self, value_dict):
        """Makes list in dict into a delimited string"""
        for i in value_dict:
            if type(value_dict[i]) is list:
                value_dict[i] = self.delimiter.join([str(x) for x in value_dict[i]]) # Join by ␞
        return value_dict

    def db_to_list(self, db_result):
        """Converts tuple from SQL query into a list"""
        if db_result == None:
            return None
        db_result = list(db_result)
        for i,j in enumerate(db_result):
            if bool(re.search(self.delimiter, str(db_result[i]))):
                db_result[i] = j.split(self.delimiter)
        del db_result[-1] # Remove key
        return db_result

    def db_add(self, table_name, value_dict):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        value_dict = self.dict_to_db(value_dict)
        # RISK FOR SQL INJECTION, BEWARE
        c.execute('''CREATE TABLE IF NOT EXISTS {} {}'''.format(table_name,
                                                                str(tuple(value_dict))))
        # This is just stupid....
        c.execute("INSERT INTO {} VALUES {}".format(table_name,
                                                    str(tuple(value_dict.values()))))
        conn.commit()
        conn.close()

    def db_find(self, table_name, key):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM {} WHERE KEY="{}"'.format(table_name, key))
        db_result = self.db_to_list(c.fetchone())
        conn.close()
        return db_result

    def db_clear(self, table_name, key):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM {} WHERE KEY="{}"'.format(table_name, key))
        conn.commit()
        conn.close()
        return 0
