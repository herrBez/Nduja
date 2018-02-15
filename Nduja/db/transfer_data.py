import sqlite3
from sqlite3 import Error
from sqlite3 import Cursor
import traceback
import os


def transfer_data(old_db : str, new_db : str) -> None:
    old = sqlite3.connect(old_db)
    new = sqlite3.connect(new_db)
    c_new = new.cursor()
    c_new = init_db(c_new)
    cold = old.cursor()
    id_info = {}
    cold.execute("SELECT * FROM Information")
    for row in cold:
        c_new.execute('''INSERT INTO Information(Name, Website, Email, Json)
                VALUES (?,?,?,?)''', (row[1], row[2], row[3], row[4],))
        c_new.execute('SELECT max(_id) FROM Information')
        id_info[row[0]] = c_new.fetchone()[0]
    new.commit()
    cold.execute("SELECT * FROM Account")
    id_account = {}
    for row in cold:
        c_new.execute("SELECT _id FROM Account WHERE Host = ? AND Username = ?",
                     (row[1], row[2],))
        data = c_new.fetchone()
        if data is None:
            newid = None
            try:
                newid = id_info[row[3]]
            except KeyError:
                print()
            c_new.execute('''INSERT INTO Account(Host, Username, Info)
                         VALUES (?,?,?)''', (row[1], row[2], newid,))
            c_new.execute('SELECT max(_id) FROM Account')
            id_account[row[0]] = c_new.fetchone()[0]
        else:
            id_account[row[0]] = data[0]
    new.commit()
    cold.execute("SELECT * FROM AccountWallet")
    for row in cold:
        try:
            c_new.execute('''SELECT * FROM AccountWallet WHERE Account = ?
                            AND Wallet = ?''', (row[1], row[2],))
            data = c_new.fetchone()
            if data is None:
                c_new.execute('''INSERT INTO AccountWallet(Account, Wallet,
                                RawURL) VALUES (?,?,?)''',
                             (str(id_account[row[1]]), row[2], row[3],))
        except Error:
            traceback.print_exc()
    new.commit()
    cold.execute("SELECT * FROM Wallet")
    for row in cold:
        try:
            c_new.execute('''INSERT INTO Wallet(Address, Currency, Status,
                            Inferred) VALUES (?,?,?,?)''',
                         (row[0], row[1], row[2], row[3],))
        except Error:
            traceback.print_exc()
    c_new.execute('''DELETE FROM Information WHERE Information._id NOT IN (
                    SELECT Account.Info FROM Account
                    WHERE Account.Info NOTNULL)''')
    new.commit()
    new.close()
    old.close()


def init_db(c : Cursor) -> Cursor:
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
                try:
                    c.execute('''INSERT INTO Wallet(Address, Currency, Status,
                                 Inferred) VALUES (?,?,?,?)''',
                              (str(w), "BTC", "-1", 0,))
                except Error:
                    traceback.print_exc()
    except Error:
        print()
    return c
