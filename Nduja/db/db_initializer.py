"""Module for initialize the database"""
import os
import json
import traceback
import sqlite3
from sqlite3 import Error


class DbInitializer:
    """Class that performs the initialization of the databas"""

    def init_db(self, db_name: str, format_file: str) -> None:
        """Method to initialize the database"""
        conn = sqlite3.connect(db_name)
        db_conn = conn.cursor()
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Currency(
                               Name VARCHAR(4) PRIMARY KEY
                           )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Wallet(
                               Address VARCHAR(128) PRIMARY KEY,
                               Currency VARCHAR(4),
                               Status NUMERIC,
                               Inferred NUMERIC,
                               FOREIGN KEY (Currency) REFERENCES Currency(Name)
                           )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Information(
                               _id INTEGER PRIMARY KEY,
                               Name TEXT,
                               Website TEXT,
                               Email TEXT,
                               Json LONGTEXT
                           )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS Account(
                               _id INTEGER PRIMARY KEY,
                               Host VARCHAR(255),
                               Username VARCHAR(255),
                               Info INT,
                               FOREIGN KEY (Info) REFERENCES Information(ID)
                           )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS AccountWallet(
                               _id INTEGER PRIMARY KEY,
                               Account INT,
                               Wallet VARCHAR(128),
                               RawURL VARCHAR(500),
                               FOREIGN KEY (Account) REFERENCES Account(ID),
                               FOREIGN KEY (Wallet) REFERENCES Wallet(Address)
                           )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS AccountRelated(
                               Account1 INT,
                               Account2 INT,
                               FOREIGN KEY (Account1) REFERENCES Account(_id),
                               FOREIGN KEY (Account2) REFERENCES Account(_id)
                           )''')
        try:
            with open(format_file, 'r') as file:
                content = file.read()
                content_json = json.loads(content)
                for obj in content_json:
                    currency_symbol = obj["symbol"]
                    db_conn.execute('''INSERT INTO Currency VALUES (?)''',
                                    (currency_symbol,))
        except Error:
            traceback.print_exc()

        try:
            path = os.path.dirname(os.path.abspath(__file__))
            with open(path + '/known_addresses_btc', 'r') as btcwallets:
                for wall in btcwallets.readlines():
                    db_conn.execute('''INSERT INTO Wallet(Address, Currency,
                                       Status, Inferred) VALUES (?,?,?,?)''',
                                    (str(wall).strip(), 'BTC', -1, 0,))
        except Error:
            traceback.print_exc()
        conn.commit()
        conn.close()
