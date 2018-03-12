import os
import sqlite3
import traceback
from sqlite3 import Error
from dao.account import Account
from dao.wallet import Wallet
from graph.cluster import Cluster
from db.db_initializer import DbInitializer

from typing import List, Iterable, Optional, Set


class DbManager:

    config = 'format.json'
    db = 'db.db'
    instance = None

    @staticmethod
    def set_config_file(filename: str):
        DbManager.config = filename

    @staticmethod
    def set_db_file_name(filename: str):
        DbManager.db = filename

    @staticmethod
    def get_instance():
        if DbManager.instance is None:
            DbManager.instance = DbManager()
        return DbManager.instance

    def __init__(self) -> None:
        self.conn = None  # type: Optional[sqlite3.Connection]
        DbInitializer().init_db(DbManager.db, DbManager.config)

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
        int_inferred = 1 if inferred else 0  # type: int

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
                                      str(email), str([json]),))
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
        info = self.insert_information(name, website, email, str([json]))  # type: int
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

    def get_all_known_wallets_by_currency(self, currency: str) -> List[Wallet]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT * FROM Wallet WHERE Status<0 AND Currency=(?)''',
                      (currency,))
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

    def find_accounts_by_wallet(self, wallet: Wallet) -> List[int]:
        c = self.conn.cursor()
        accounts = []
        try:
            c.execute('''SELECT AccountWallet.Account 
                         FROM AccountWallet INNER JOIN Wallet
                         WHERE AccountWallet.Wallet = Wallet.Address AND
                         AccountWallet.Wallet = ? AND
                         Wallet.Currency = ?''',
                      (wallet.address, wallet.currency))
            for row in c:
                accounts.append(row[0])
        except Error:
            traceback.print_exc()
        return accounts

    def insert_clusters(self, clusters: Iterable[Cluster]) -> None:
        c = self.conn.cursor()
        for cluster in clusters:
            accounts = set([])
            for wallet in cluster.original_addresses:
                account_related = self.find_accounts_by_wallet(wallet)
                accounts.update(set(account_related))
                print(str(wallet))
                assert len(account_related) > 0
                assert self.find_wallet(wallet.address)
            first_addr = accounts.pop()
            accounts.add(first_addr)
            for wallet in cluster.inferred_addresses:
                acc = self.find_accounts_by_wallet(wallet)
                if len(acc) > 0:
                    accounts.update(acc)
                else:
                    self.insert_wallet_with_account(wallet.address,
                                                    wallet.currency,
                                                    wallet.status,
                                                    first_addr, "",
                                                    wallet.inferred == 1)
            if len(accounts) > 1:
                accounts.remove(first_addr)
                for account in accounts:
                    c.execute('''INSERT INTO AccountRelated(Account1, Account2) 
                                 VALUES (?,?)''', (first_addr, account,))

    def retrieve_clusters_by_currency(self, currency: str) -> Iterable[Cluster]:
        c = self.conn.cursor()
        c.execute('''SELECT _id FROM Account''')
        accounts = set([])  # type: Set[int]
        for row in c:
            accounts.add(row[0])
        clusters = set([])  # type: Set[Cluster]
        for account in accounts:
            c.execute('''SELECT Wallet.Address, Wallet.Currency, Wallet.Status,
                         Wallet.Inferred 
                         FROM AccountWallet INNER JOIN Wallet
                         WHERE AccountWallet.Wallet = Wallet.Address AND
                         AccountWallet.Account=(?) AND Wallet.Currency = (?)''',
                      (account, currency,))
            wallets = set([])  # type: Set[Wallet]
            for row in c:
                wallets.add(Wallet(row[0], row[1], row[2], row[3]))
            original_addresses = [w for w in wallets if not w.inferred]
            clusters.add(Cluster(original_addresses, None, wallets, [account]))

        # take all account related by the first of the 2 accounts
        accounts_related = set([])
        c.execute('''SELECT Account1 FROM AccountRelated''')
        for row in c:
            accounts_related.add(row[0])
        for acc_1 in accounts_related:
            clusters_acc_1 = set([])
            # find all cluster related to a certain account
            # generic, in must be only one
            for cluster in clusters:
                if acc_1 in cluster.ids:
                    clusters_acc_1.add(cluster)
            # remove those clusters from the set to be returned
            clusters = clusters.difference(clusters_acc_1)
            clusters_acc_1_list = list(clusters_acc_1)
            cluster_merged = clusters_acc_1_list[0]  # type: Cluster
            cluster_to_merge = set(clusters_acc_1_list[1:])
            # take all account related to acc_1
            c.execute('''SELECT Account2 FROM AccountRelated
                         WHERE Account1 = (?)''', (acc_1,))
            accs_2 = set([])
            for row in c:
                accs_2.add(row[0])
            # find cluster related to accounts related to acc_1
            for cluster in clusters:
                if accs_2.intersection(set(cluster.ids)):
                    cluster_to_merge.add(cluster)
            # merge those clusters removing them from the cluster to be returned
            for cluster in cluster_to_merge:
                if cluster in clusters:
                    clusters.remove(cluster)
                cluster_merged.merge(cluster)
            clusters.add(cluster_merged)
        return clusters

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
