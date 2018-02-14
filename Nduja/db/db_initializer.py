import sqlite3
from sqlite3 import Error
import os


class DbInitializer:
    def init_db(self, db_name : str) -> None:
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
                     FOREIGN KEY Account1 REFERENCES Account(_id)
                     FOREIGN KEY Account2 REFERENCES Account(_id)
                     )''')
        try:
            c.execute('''INSERT INTO Currency VALUES ("BTC")''')
            c.execute('''INSERT INTO Currency VALUES ("ETH")''')
            c.execute('''INSERT INTO Currency VALUES ("ETC")''')
            c.execute('''INSERT INTO Currency VALUES ("XMR")''')
            c.execute('''INSERT INTO Currency VALUES ("BCH")''')
            c.execute('''INSERT INTO Currency VALUES ("LTC")''')
            c.execute('''INSERT INTO Currency VALUES ("DOGE")''')
        except Error:
            print()
        try:
            path = os.path.dirname(os.path.abspath(__file__))
            with open(path + '/known_addresses_btc', 'r') as btcwallets:
                for w in btcwallets.readlines():
                    c.execute('''INSERT INTO Wallet(Address, Currency, Status)
                                 VALUES (?,?,?,?)''', (str(w), 'BTC', -1,))
        except Error:
            print()
        conn.commit()
        conn.close()
