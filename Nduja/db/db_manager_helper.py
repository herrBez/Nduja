from typing import List
from typing import Iterable

import json
import sqlite3
import traceback
from sqlite3 import Error
import os
from dao.wallet import Wallet


class DbManager2:

    def __init__(self, db_name: str) -> None:
        self.conn = None
        self.db = db_name
        self.init_connection()
        self.init_db(db_name)

    def init_db(self, db_name: str) -> None:
        self.conn = sqlite3.connect(db_name)
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS AddressProcessed (
                        Address VARCHAR(128) PRIMARY KEY,
                        Currency VARCHAR(4),
                        Status NUMERIC,
                        Inferred NUMERIC
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS AddressToProcess (
                        Address VARCHAR(128) PRIMARY KEY,
                        Currency VARCHAR(4),
                        Status NUMERIC,
                        Inferred NUMERIC
                    )''')
        self.conn.commit()
        self.conn.close()

    def init_connection(self) -> None:
        self.conn = sqlite3.connect(self.db)

    def close_db(self) -> None:
        self.conn.close()

    def save_changes(self) -> None:
        self.conn.commit()

    def save_and_close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def insert_processed(self, wallets: List[Wallet]) -> bool:
        c = self.conn.cursor()
        for wallet in wallets:
            try:
                c.execute('''INSERT INTO AddressProcessed(Address, Currency,
                             Status, Inferred) VALUES (?, ?, ?, ?)''',
                          (str(wallet.address), str(wallet.currency),
                           wallet.status, wallet.inferred))
            except Error:
                traceback.print_exc()
                return False
        return True

    def insert_to_process(self, wallets: List[Wallet]) -> bool:
        c = self.conn.cursor()
        for wallet in wallets:
            try:
                c.execute('''INSERT INTO AddressToProcess(Address, Currency,
                             Status, Inferred) VALUES (?, ?, ?, ?)''',
                          (str(wallet.address), str(wallet.currency),
                           wallet.status, wallet.inferred))
            except Error:
                traceback.print_exc()
                return False
        return True

    def wallets_processed(self) -> List[Wallet]:
        c = self.conn.cursor()
        wallets = []
        try:
            c.execute('''SELECT * FROM AddressProcessed''')
            for row in c:
                wallets.append(Wallet(row[0], row[1], '', row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets

    def wallets_to_process(self) -> List[str]:
        c = self.conn.cursor()
        wallets = []
        try:
            c.execute('''SELECT * FROM AddressToProcess''')
            for row in c:
                wallets.append(Wallet(row[0], row[1], '', row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets

    def remove_to_process_wallets(self, wallets: List[Wallet]) -> None:
        c = self.conn.cursor()
        for w in wallets:
            try:
                c.execute('''DELETE FROM AddressToProcess WHERE 
                            Address = (?)''', (w.address,))
            except Error:
                traceback.print_exc()