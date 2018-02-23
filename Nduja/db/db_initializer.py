import json
import sqlite3
import traceback
from sqlite3 import Error
import os


class DbInitializer:
    def init_db(self, db_name: str, format_file: str) -> None:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Currency(
                    Name VARCHAR(4) PRIMARY KEY
                )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Wallet(
                    Address VARCHAR(128) PRIMARY KEY,
                    Currency VARCHAR(4),
                    Status NUMERIC,
                    Inferred NUMERIC,
                    FOREIGN KEY (Currency) REFERENCES Currency(Name)
                )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Information(
                    _id INTEGER PRIMARY KEY,
                    Name TEXT,
                    Website TEXT,
                    Email TEXT,
                    Json LONGTEXT
                )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Account(
                    _id INTEGER PRIMARY KEY,
                    Host VARCHAR(255),
                    Username VARCHAR(255),
                    Info INT,
                    FOREIGN KEY (Info) REFERENCES Information(ID)
                )''')
        c.execute('''CREATE TABLE IF NOT EXISTS AccountWallet(
                    _id INTEGER PRIMARY KEY,
                    Account INT,
                    Wallet VARCHAR(128),
                    RawURL VARCHAR(500),
                    FOREIGN KEY (Account) REFERENCES Account(ID),
                    FOREIGN KEY (Wallet) REFERENCES Wallet(Address)
                )''')
        c.execute('''CREATE TABLE IF NOT EXISTS AccountRelated(
                     Account1 INT,
                     Account2 INT,
                     FOREIGN KEY (Account1) REFERENCES Account(_id),
                     FOREIGN KEY (Account2) REFERENCES Account(_id)
                     )''')
        try:
            with open(format_file, 'r') as format:
                content = format.read()
                content_json = json.loads(content)
                for obj in content_json:
                    currency_symbol = obj["symbol"]
                    c.execute('''INSERT INTO Currency VALUES (?)''',
                              (currency_symbol,))
        except Error:
            traceback.print_exc()

        try:
            path = os.path.dirname(os.path.abspath(__file__))
            with open(path + '/known_addresses_btc', 'r') as btcwallets:
                for w in btcwallets.readlines():
                    c.execute('''INSERT INTO Wallet(Address, Currency, Status, 
                                 Inferred) VALUES (?,?,?,?)''',
                              (str(w).strip(), 'BTC', -1, 0,))
        except Error:
            traceback.print_exc()
        conn.commit()
        conn.close()
