import sqlite3
from sqlite3 import Error
from dao.account import Account
import traceback


class DbManager:
    conn = None
    db = 'db.db'
    instance = None

    def setDBFileName(filename):
        DbManager.db = filename

    def getInstance():
        if DbManager.instance is None:
            DbManager.instance = DbManager()
        return DbManager.instance

    def __init__(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Currency(
            Name VARCHAR(4) PRIMARY KEY
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Wallet(
            Address VARCHAR(128) PRIMARY KEY,
            Currency VARCHAR(4),
            Status NUMERIC,
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
            traceback.print_exc()

    def initConnection(self):
        self.conn = sqlite3.connect(DbManager.db)

    def saveChanges(self):
        self.conn.commit()
        self.conn.close()

    def insertWallet(self, address, currency, status):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Status)
                VALUES (?,?,?)''', (str(address), str(currency), status,))
        except Error:
            traceback.print_exc()
            return False
        return True

    def insertWalletWithAccount(self, address, currency, status, account, url):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Status)
                VALUES (?,?,?)''', (str(address), str(currency), status,))
        except Error:
            traceback.print_exc()
            return False
        return self.insertAccountWallet(account, address, url)

    def insertInformation(self, name, website, email, json):
        c = self.conn.cursor()
        if (email is None or email.isspace()):
            email = " "
        try:
            c.execute('''INSERT INTO Information(Name, Website, Email, Json)
                VALUES (?,?,?,?)''', (str(name), str(website),
                                      str(email), str(json),))
        except Error:
            traceback.print_exc()
            return -1
        c.execute('SELECT max(_id) FROM Information')
        max_id = c.fetchone()[0]
        return max_id

    def insertAccount(self, host, username, info):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Account(Host, Username, Info)
                VALUES (?,?,?)''', (str(host), str(username), info,))
        except Error:
            traceback.print_exc()
            return -1
        c.execute('SELECT max(_id) FROM Account')
        max_id = c.fetchone()[0]
        return max_id

    def insertAccountNoInfo(self, host, username):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO Account(Host, Username)
                VALUES (?,?)''', (str(host), str(username),))
        except Error:
            traceback.print_exc()
            return -1
        c.execute('SELECT max(_id) FROM Account')
        max_id = c.fetchone()[0]
        return max_id

    def insertAccountWallet(self, account, wallet, url):
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO AccountWallet(Account, Wallet, RawURL)
                VALUES (?,?,?)''', (account, str(wallet), url,))
        except Error:
            traceback.print_exc()
            return -1
        c.execute('SELECT max(_id) FROM AccountWallet')
        max_id = c.fetchone()[0]
        return max_id

    def findWallet(self, address):
        c = self.conn.cursor()
        c.execute("SELECT * FROM Wallet WHERE address = ?", (address,))
        data = c.fetchone()
        self.conn.close()
        return (data is not None)

    def findAccount(self, host, username):
        c = self.conn.cursor()
        c.execute("SELECT _id FROM Account WHERE Host = ? AND Username = ?",
                  (host, username,))
        data = c.fetchone()
        self.conn.close()
        if data is None:
            return -1
        else:
            return data[0]

    def insertNewInfo(self, address, currency, status, name, website, email,
                      json, host, username, url):
        self.insertWallet(address, currency, status)
        info = self.insertInformation(name, website, email, json)
        acc = self.insertAccount(host, username, info)
        self.insertAccountWallet(acc, address, url)
        return acc

    def insertMultipleAddresses(self, acc, wallets):
        for wallet in wallets:
            self.insertWallet(wallet.address, wallet.currency, wallet.status)
            self.insertAccountWallet(acc, wallet.address, wallet.file)

    def getAllAccounts(self):
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Account''')
            for row in c:
                accounts.append(Account(row[0], row[1], row[2], row[3]))
        except Error:
            traceback.print_exc()
        return accounts

    def addInfoToAccount(self, accountId, infoId):
        c = self.conn.cursor()
        try:
            c.execute('''UPDATE Account SET Info = ? WHERE _id = ?''',
                      (infoId, accountId,))
        except Error:
            traceback.print_exc()
            return False
        return True

# try:
#     os.remove('./db.db')
# except OSError:
#     pass
# manager = DbManager()
# manager.insertWallet("aaa", "BTC", "NA")
# info = manager.insertInformation("nome", "sito", "email", "json")
# acc = manager.insertAccount("host", "user", info)
# manager.insertAccountWallet(acc, "aaa", "file")
# acc2 = manager.insertNewInfo('bbb2', 'ETH', 'SI', 'nome cognome2',
#                                'sito.com2', 'email2', 'json2', 'host2',
#                                'username2', 'path2')
# x = [Wallet('bbb21', 'BTC', 'path21', 'NA'),
#      Wallet('bbb22', 'BCH', 'path22', 'NO')]
# manager.insertMultipleAddresses(acc2, x)
#
