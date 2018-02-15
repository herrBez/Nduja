import os
import sqlite3
import traceback
from sqlite3 import Error
from dao.account import Account
from dao.wallet import Wallet

from typing import List



class DbManager:

    db = 'db.db'
    instance = None

    @staticmethod
    def set_db_file_name(filename: str):
        DbManager.db = filename

    @staticmethod
    def get_instance():
        if DbManager.instance is None:
            DbManager.instance = DbManager()
        return DbManager.instance

    def __init__(self) -> None:
        self.init_connection()
        c = self.conn.cursor()
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
                    self.insert_wallet(str(w), "BTC", -1)
        except Error:
            traceback.print_exc()
        self.save_changes()

    def init_connection(self) -> None:
        self.conn = sqlite3.connect(DbManager.db)

    def close_db(self) -> None:
        self.conn.close()

    def save_changes(self) -> None:
        self.conn.commit()
        self.conn.close()

    def insert_wallet(self, address: str, currency: str, status: int,
                      inferred: bool = False) -> bool:
        c = self.conn.cursor()
        int_inferred = 1 if inferred else 0  # type: int
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Status, Inferred)
                VALUES (?,?,?,?)''', (str(address), str(currency), status,
                                      int_inferred,))
        except Error:
            traceback.print_exc()
            return False
        return True

    def insert_wallet_with_account(self, address: str, currency: str,
                                   status: int, account: int, url: str,
                                   inferred: bool = False) -> bool:
        c = self.conn.cursor()
        int_inferred = 1 if inferred else 0 # type: int
        try:
            c.execute('''INSERT INTO Wallet(Address, Currency, Status, Inferred)
                VALUES (?,?,?,?)''', (str(address), str(currency), status,
                                      int_inferred,))
        except Error:
            traceback.print_exc()
            return False

        return self.insert_account_wallet(account, address, url) >= 0

    def insert_information(self, name: str, website: str, email: str,
                           json: str) -> int:
        c = self.conn.cursor()
        if email is None or email.isspace():
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

    def insert_account(self, host: str, username: str, info: int) -> int:
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

    def insert_account_no_info(self, host: str, username: str) -> int:
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

    def insert_account_wallet(self, account: int, wallet: str, url: str) -> int:
        c = self.conn.cursor()
        try:
            c.execute('''INSERT INTO AccountWallet(Account, Wallet, RawURL)
                VALUES (?,?,?)''', (account, wallet, url,))
        except Error:
            traceback.print_exc()
            return -1
        c.execute('SELECT max(_id) FROM AccountWallet')
        max_id = c.fetchone()[0]
        return max_id

    def find_wallet(self, address: str) -> bool:
        c = self.conn.cursor()
        c.execute("SELECT * FROM Wallet WHERE address = ?", (address,))
        data = c.fetchone()
        return data is not None

    def find_account(self, host: str, username: str) -> int:
        c = self.conn.cursor()
        c.execute("SELECT _id FROM Account WHERE Host = ? AND Username = ?",
                  (host, username,))
        data = c.fetchone()
        if data is None:
            return -1
        else:
            return data[0]

    def insert_new_info(self, address: str, currency: str, status: int,
                        name: str, website: str, email: str, json: str,
                        host: str, username: str, url: str):

        self.insert_wallet(address, currency, status)
        info = self.insert_information(name, website, email, json)  # type: int
        acc = self.insert_account(host, username, info)
        self.insert_account_wallet(acc, address, url)
        return acc

    def insert_multiple_addresses(self, acc: int,
                                  wallets: List[Wallet]) -> None:
        for wallet in wallets:
            self.insert_wallet(wallet.address, wallet.currency, wallet.status)
            self.insert_account_wallet(acc, wallet.address, wallet.file)

    def get_all_accounts(self) -> List[Account]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Account''')
            for row in c:
                accounts.append(Account(row[0], row[1], row[2], row[3]))
        except Error:
            traceback.print_exc()
        return accounts

    def add_info_to_account(self, accountId: int, infoId: int) -> bool:
        c = self.conn.cursor()
        try:
            c.execute('''UPDATE Account SET Info = ? WHERE _id = ?''',
                      (infoId, accountId,))
        except Error:
            traceback.print_exc()
            return False
        return True

    def get_all_wallets(self) -> List[Wallet]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Wallet WHERE Status>=0''')
            for row in c:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_wallets_by_currency(self, currency : str) -> List[Wallet]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Wallet WHERE Status>=0 
                      AND Currency = ?''', (currency,))
            for row in c:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_known_wallets(self) -> List[Wallet]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Wallet WHERE Status<0''')
            for row in c:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_inferred_wallets(self) -> List[Wallet]:
        c = self.conn.cursor()
        wallets = []
        try:
            c.execute('''SELECT * FROM Wallet WHERE Inferred!=0''')
            for row in c:
                wallets.append(Wallet(row[0], row[1], None, row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets


# try:
#     os.remove('./db.db')
# except OSError:
#     pass
# DbManager.setDBFileName('attempt')
# manager = DbManager.getInstance()
# manager.initConnection()
# manager.insertWallet("aaa", "BTC", 1)
# info = manager.insertInformation("nome", "sito", "email", "json")
# acc = manager.insertAccount("host", "user", info)
# manager.insertAccountWallet(acc, "aaa", "file")
# acc2 = manager.insertNewInfo('bbb2', 'ETH', 1, 'nome cognome2',
#                              'sito.com2', 'email2', 'json2', 'host2',
#                              'username2', 'path2')
# x = [Wallet('bbb21', 'BTC', 'path21', 0, False),
#      Wallet('bbb22', 'BCH', 'path22', 1, True)]
# for w in x:
#     print(w)
# manager.insertMultipleAddresses(acc2, x)
# manager.saveChanges()
#
