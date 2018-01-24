import sqlite3
from sqlite3 import Error
import os


class DbManager:
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Currency(
            Name VARCHAR(4) PRIMARY KEY
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Wallet(
            Address VARCHAR(128) PRIMARY KEY,
            Currency VARCHAR(4),
            Used VARCHAR(2),
            FOREIGN KEY (Currency) REFERENCES Currency(Name)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Information(
            _id INTEGER PRIMARY KEY,
            Name VARCHAR(255),
            Website VARCHAR(255),
            Email VARCHAR(255),
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
            PathToFile VARCHAR(255),
            FOREIGN KEY (Account) REFERENCES Account(ID),
            FOREIGN KEY (Wallet) REFERENCES Wallet(Address)
        )''')
        c.execute('''INSERT INTO Currency VALUES ("BTC")''')
        c.execute('''INSERT INTO Currency VALUES ("ETH")''')
        c.execute('''INSERT INTO Currency VALUES ("ETC")''')
        c.execute('''INSERT INTO Currency VALUES ("XMR")''')
        c.execute('''INSERT INTO Currency VALUES ("BCH")''')
        c.execute('''INSERT INTO Currency VALUES ("LTC")''')
        c.execute('''INSERT INTO Currency VALUES ("DOGE")''')
        self.conn.commit()
        self.conn.close()

    def insertWallet(self, address, currency, used):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Used)
                VALUES (?,?,?)''', (address, currency, used,))
        except Error:
            return False
        self.conn.commit()
        self.conn.close()
        return True

    def insertWalletWithAccount(self, address, currency, used, account, path):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Used)
                VALUES (?,?,?)''', (address, currency, used,))
        except Error:
            return False
        self.conn.commit()
        self.conn.close()
        return self.insertAccountWallet(account, address, path)

    def insertInformation(self, name, website, email, json):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Information(Name, Website, Email, Json)
                VALUES (?,?,?,?)''', (name, website, email, json,))
        except Error:
            return -1
        c.execute('SELECT max(_id) FROM Information')
        max_id = c.fetchone()[0]
        self.conn.commit()
        self.conn.close()
        return max_id

    def insertAccount(self, host, username, info):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Account(Host, Username, Info)
                VALUES (?,?,?)''', (host, username, info,))
        except Error:
            return -1
        c.execute('SELECT max(_id) FROM Account')
        max_id = c.fetchone()[0]
        self.conn.commit()
        self.conn.close()
        return max_id

    def insertAccountNoInfo(self, host, username):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Account(Host, Username)
                VALUES (?,?)''', (host, username,))
        except Error:
            print()
            return -1
        c.execute('SELECT max(_id) FROM Account')
        max_id = c.fetchone()[0]
        self.conn.commit()
        self.conn.close()
        return max_id

    def insertAccountWallet(self, account, wallet, path):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO AccountWallet(Account, Wallet, PathToFile)
                VALUES (?,?,?)''', (account, wallet, path,))
        except Error:
            return -1
        c.execute('SELECT max(_id) FROM AccountWallet')
        max_id = c.fetchone()[0]
        self.conn.commit()
        self.conn.close()
        return max_id

    def findWallet(self, address):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        c.execute("SELECT * FROM Wallet WHERE address = ?", (address,))
        data = c.fetchone()
        self.conn.close()
        return (data is None)

    def findAccount(self, host, username):
        self.conn = sqlite3.connect('db.db')
        c = self.conn.cursor()
        c.execute("SELECT _id FROM Account WHERE Host = ? AND Username = ?",
                  (host, username,))
        data = c.fetchone()
        self.conn.close()
        if data is None:
            return -1
        else:
            return data[0]

    def insertNewInfo(self, address, currency, used, name, website, email,
                      json, host, username, path):
        self.insertWallet(address, currency, used)
        info = self.insertInformation(name, website, email, json)
        acc = self.insertAccount(host, username, info)
        self.insertAccountWallet(acc, address, path)
        return acc

    def insertMultipleAddresses(self, acc, wallets):
        for wallet in wallets:
            self.insertWallet(wallet.address, wallet.currency, wallet.used)
            self.insertAccountWallet(acc, wallet.address, wallet.file)


class Wallet:
    address = None
    currency = None
    used = None
    file = None

    def __init__(self, add, curr, f, u):
        self.address = add
        self.currency = curr
        self.file = f
        self.used = u


# try:
#     os.remove('./db.db')
# except OSError:
#     pass
# manager = DbManager()
# manager.insertWallet("aaa", "BTC", "NA")
# info = manager.insertInformation("nome", "sito", "email", "json")
# acc = manager.insertAccount("host", "user", info)
# manager.insertAccountWallet(acc, "aaa", "file")
# acc2 = manager.insertNewInfo('bbb2', 'ETH', 'SI', 'nome cognome2', 'sito.com2',
#                              'email2', 'json2', 'host2', 'username2', 'path2')
# x = [Wallet('bbb21', 'BTC', 'path21', 'NA'),
#      Wallet('bbb22', 'BCH', 'path22', 'NO')]
# manager.insertMultipleAddresses(acc2, x)
#
