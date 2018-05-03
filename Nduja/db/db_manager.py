"""Module for managing database"""
from typing import List, Iterable, Optional, Set

import sqlite3
from sqlite3 import Error
import traceback

from dao.account import Account
from dao.wallet import Wallet
from graph.cluster import Cluster
from db.db_initializer import DbInitializer


class DbManager:
    """Class that offers method to query the db"""
    config = 'format.json'
    db = 'db.db'
    instance = None

    @staticmethod
    def set_config_file(filename: str):
        """Method to set the configuration file"""
        DbManager.config = filename

    @staticmethod
    def set_db_file_name(filename: str):
        """Method to set the database file name"""
        DbManager.db = filename

    @staticmethod
    def get_instance():
        """Method to retrieve an instance of thedatabase manager"""
        if DbManager.instance is None:
            DbManager.instance = DbManager()
        return DbManager.instance

    def __init__(self) -> None:
        self.conn = None  # type: Optional[sqlite3.Connection]
        DbInitializer().init_db(DbManager.db, DbManager.config)

    def init_connection(self) -> None:
        """Method to open the database"""
        self.conn = sqlite3.connect(DbManager.db)

    def close_db(self) -> None:
        """Method to close the database"""
        self.conn.close()

    def save_changes(self) -> None:
        """Method to save changes and close the database"""
        self.conn.commit()
        self.conn.close()

    def insert_wallet(self, address: str, currency: str, status: int,
                      inferred: bool = False) -> bool:
        """Method to insert a new wallet into the database"""
        db_conn = self.conn.cursor()
        int_inferred = 1 if inferred else 0  # type: int
        try:
            db_conn.execute('''INSERT INTO Wallet(Address, Currency, Status,
                               Inferred) VALUES (?,?,?,?)''',
                            (str(address), str(currency), status, int_inferred))
        except Error:
            traceback.print_exc()
            return False
        return True

    def insert_wallet_with_account(self, address: str, currency: str,
                                   status: int, account: int, url: str,
                                   inferred: bool = False) -> bool:
        """Method to insert a new wallet into the database connected to a
        certain accoint"""
        db_conn = self.conn.cursor()
        int_inferred = 1 if inferred else 0  # type: int

        try:
            db_conn.execute('''INSERT INTO Wallet(Address, Currency, Status,
                               Inferred) VALUES (?,?,?,?)''',
                            (str(address), str(currency), status, int_inferred))
        except Error:
            traceback.print_exc()
            return False

        return self.insert_account_wallet(account, address, url) >= 0

    def insert_information(self, name: str, website: str, email: str,
                           json: str) -> int:
        """Method to insert a new information into the database"""
        db_conn = self.conn.cursor()
        if email is None or email.isspace():
            email = " "
        try:
            db_conn.execute('''INSERT INTO Information(Name, Website, Email,
                               Json) VALUES (?,?,?,?)''',
                            (str(name), str(website), str(email), str([json]),))
        except Error:
            traceback.print_exc()
            return -1
        db_conn.execute('SELECT max(_id) FROM Information')
        max_id = db_conn.fetchone()[0]
        return max_id

    def insert_account(self, host: str, username: str, info: int) -> int:
        """Method to insert a new account into the database"""
        db_conn = self.conn.cursor()
        try:
            db_conn.execute('''INSERT INTO Account(Host, Username, Info)
                               VALUES (?,?,?)''',
                            (str(host), str(username), info,))
        except Error:
            traceback.print_exc()
            return -1
        db_conn.execute('SELECT max(_id) FROM Account')
        max_id = db_conn.fetchone()[0]
        return max_id

    def insert_account_no_info(self, host: str, username: str) -> int:
        """Method to insert a new account not connected to an information object
        into the database"""
        db_conn = self.conn.cursor()
        try:
            db_conn.execute('''INSERT INTO Account(Host, Username)
                VALUES (?,?)''', (str(host), str(username),))
        except Error:
            traceback.print_exc()
            return -1
        db_conn.execute('SELECT max(_id) FROM Account')
        max_id = db_conn.fetchone()[0]
        return max_id

    def insert_account_wallet(self, account: int, wallet: str, url: str) -> int:
        """Method to insert a new account-wallet into the database"""
        db_conn = self.conn.cursor()
        try:
            db_conn.execute('''INSERT INTO AccountWallet(Account, Wallet,
                               RawURL) VALUES (?,?,?)''',
                            (account, wallet, url,))
        except Error:
            traceback.print_exc()
            return -1
        db_conn.execute('SELECT max(_id) FROM AccountWallet')
        max_id = db_conn.fetchone()[0]
        return max_id

    def find_wallet(self, address: str) -> bool:
        """Method to search a wallet into the database"""
        db_conn = self.conn.cursor()
        db_conn.execute("SELECT * FROM Wallet WHERE address = ?", (address,))
        data = db_conn.fetchone()
        return data is not None

    def find_account(self, host: str, username: str) -> int:
        """Method to search an account into the database, if found returns the
        id, -1 otherwise"""
        db_conn = self.conn.cursor()
        db_conn.execute("SELECT _id FROM Account WHERE Host = ? AND "
                        "Username = ?", (host, username,))
        data = db_conn.fetchone()
        if data is None:
            return -1
        return data[0]

    def insert_new_info(self, address: str, currency: str, status: int,
                        name: str, website: str, email: str, json: str,
                        host: str, username: str, url: str):
        """Method to insert an account connected with a wallet into the
        database"""
        self.insert_wallet(address, currency, status)
        info = self.insert_information(name, website, email, str([json]))  # type: int
        acc = self.insert_account(host, username, info)
        self.insert_account_wallet(acc, address, url)
        return acc

    def insert_multiple_addresses(self, acc: int,
                                  wallets: List[Wallet]) -> None:
        """Method to insert a list of wallets into the database"""
        for wallet in wallets:
            self.insert_wallet(wallet.address, wallet.currency, wallet.status)
            self.insert_account_wallet(acc, wallet.address, wallet.file)

    def get_all_accounts(self) -> List[Account]:
        """Method to retrieve all accounts of the database"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT * FROM Account''')
            for row in db_conn:
                accounts.append(Account(row[0], row[1], row[2], row[3]))
        except Error:
            traceback.print_exc()
        return accounts

    def add_info_to_account(self, account_id: int, info_id: int) -> bool:
        """Method to connect an information object to a certain account into
        the database"""
        db_conn = self.conn.cursor()
        try:
            db_conn.execute('''UPDATE Account SET Info = ? WHERE _id = ?''',
                            (info_id, account_id,))
        except Error:
            traceback.print_exc()
            return False
        return True

    def get_all_wallets(self) -> List[Wallet]:
        """Method to retrieve all wallets of the database"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT * FROM Wallet WHERE Status>=0''')
            for row in db_conn:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_wallets_by_currency(self, currency: str) -> List[Wallet]:
        """Method to retrieve all wallets of the database of a certain
        currency"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT * FROM Wallet WHERE Status>=0
                      AND Currency = ?''', (currency,))
            for row in db_conn:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_known_wallets(self) -> List[Wallet]:
        """Method to retrieve all wallets with status -1 of the database"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT * FROM Wallet WHERE Status<0''')
            for row in db_conn:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_known_wallets_by_currency(self, currency: str) -> List[Wallet]:
        """Method to retrieve all wallets with status -1 of the database by
        currency"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT * FROM Wallet WHERE Status<0 AND
                               Currency=(?)''', (currency,))
            for row in db_conn:
                accounts.append(Wallet(row[0], row[1], None, row[2]))
        except Error:
            traceback.print_exc()
        return accounts

    def get_all_inferred_wallets(self) -> List[Wallet]:
        """Method to retrieve all wallets with inferred = 1 of the database"""
        db_conn = self.conn.cursor()
        wallets = []
        try:
            db_conn.execute('''SELECT * FROM Wallet WHERE Inferred!=0''')
            for row in db_conn:
                wallets.append(Wallet(row[0], row[1], None, row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets

    def find_accounts_by_wallet(self, wallet: Wallet) -> List[int]:
        """Method to retrieve accounts connected to a certain wallet of the
        database"""
        db_conn = self.conn.cursor()
        accounts = []
        try:
            db_conn.execute('''SELECT AccountWallet.Account
                               FROM AccountWallet INNER JOIN Wallet
                               WHERE AccountWallet.Wallet = Wallet.Address AND
                               AccountWallet.Wallet = ? AND
                               Wallet.Currency = ?''',
                            (wallet.address, wallet.currency))
            for row in db_conn:
                accounts.append(row[0])
        except Error:
            traceback.print_exc()
        return accounts

    def insert_clusters(self, clusters: Iterable[Cluster]) -> None:
        """Method to insert an iterable of clusters into the database"""
        db_conn = self.conn.cursor()
        for cluster in clusters:
            accounts = set([])
            for wallet in cluster.original_addresses:
                account_related = self.find_accounts_by_wallet(wallet)
                accounts.update(set(account_related))
                print(str(wallet))
                assert account_related
                assert self.find_wallet(wallet.address)
            first_addr = accounts.pop()
            accounts.add(first_addr)
            for wallet in cluster.inferred_addresses:
                acc = self.find_accounts_by_wallet(wallet)
                if acc:
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
                    db_conn.execute('''INSERT INTO AccountRelated(Account1,
                                       Account2) VALUES (?,?)''',
                                    (first_addr, account,))

    def retrieve_clusters_by_currency(self, currency: str) -> Iterable[Cluster]:
        db_conn = self.conn.cursor()
        db_conn.execute('''SELECT _id FROM Account''')
        accounts = set([])  # type: Set[int]
        for row in db_conn:
            accounts.add(row[0])
        clusters = set([])  # type: Set[Cluster]
        for account in accounts:
            db_conn.execute('''SELECT Wallet.Address, Wallet.Currency,
                               Wallet.Status, Wallet.Inferred 
                               FROM AccountWallet INNER JOIN Wallet
                               WHERE AccountWallet.Wallet = Wallet.Address AND
                               AccountWallet.Account=(?) AND
                               Wallet.Currency = (?)''',
                            (account, currency,))
            wallets = set([])  # type: Set[Wallet]
            for row in db_conn:
                wallets.add(Wallet(row[0], row[1], row[2], row[3]))
            original_addresses = [w for w in wallets if not w.inferred]
            clusters.add(Cluster(original_addresses, None, wallets, [account]))

        # take all account related by the first of the 2 accounts
        accounts_related = set([])
        db_conn.execute('''SELECT Account1 FROM AccountRelated''')
        for row in db_conn:
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
            db_conn.execute('''SELECT Account2 FROM AccountRelated
                         WHERE Account1 = (?)''', (acc_1,))
            accs_2 = set([])
            for row in db_conn:
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
