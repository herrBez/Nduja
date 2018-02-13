import sqlite3
from sqlite3 import Error
from sqlite3 import Cursor
import traceback
import os


def transfer_data(oldDb : str, newDb : str) -> None:
    old = sqlite3.connect(oldDb)
    new = sqlite3.connect(newDb)
    cnew = new.cursor()
    cnew = init_db(cnew)
    cold = old.cursor()
    idInfo = {}
    cold.execute("SELECT * FROM Information")
    for row in cold:
        cnew.execute('''INSERT INTO Information(Name, Website, Email, Json)
                VALUES (?,?,?,?)''', (row[1], row[2], row[3], row[4],))
        cnew.execute('SELECT max(_id) FROM Information')
        idInfo[row[0]] = cnew.fetchone()[0]
    new.commit()
    cold.execute("SELECT * FROM Account")
    idAccount = {}
    for row in cold:
        cnew.execute("SELECT _id FROM Account WHERE Host = ? AND Username = ?",
                     (row[1], row[2],))
        data = cnew.fetchone()
        if data is None:
            newid = None
            try:
                newid = idInfo[row[3]]
            except KeyError:
                print()
            cnew.execute('''INSERT INTO Account(Host, Username, Info)
                         VALUES (?,?,?)''', (row[1], row[2], newid,))
            cnew.execute('SELECT max(_id) FROM Account')
            idAccount[row[0]] = cnew.fetchone()[0]
        else:
            idAccount[row[0]] = data[0]
    new.commit()
    cold.execute("SELECT * FROM AccountWallet")
    for row in cold:
        try:
            cnew.execute('''SELECT * FROM AccountWallet WHERE Account = ?
                            AND Wallet = ?''', (row[1], row[2],))
            data = cnew.fetchone()
            if data is None:
                cnew.execute('''INSERT INTO AccountWallet(Account, Wallet,
                                RawURL) VALUES (?,?,?)''',
                             (str(idAccount[row[1]]), row[2], row[3],))
        except Error:
            traceback.print_exc()
    new.commit()
    cold.execute("SELECT * FROM Wallet")
    for row in cold:
        try:
            cnew.execute('''INSERT INTO Wallet(Address, Currency, Status,
                            Inferred) VALUES (?,?,?,?)''',
                         (row[0], row[1], row[2], row[3],))
        except Error:
            traceback.print_exc()
    cnew.execute('''DELETE FROM Information WHERE Information._id NOT IN (
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
