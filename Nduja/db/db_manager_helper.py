"""Module for class DbManager2 for manager auxiliary database for local
search"""
from typing import List, Optional, Iterable

import sqlite3
from sqlite3 import Error, Connection
import traceback
import os

from dao.wallet import Wallet


class DbManager2:
    """Class for manage auxiliary database for temporary save addresses to
    which search for siblings in the blockchain"""
    def __init__(self, db_name: str) -> None:
        """Constructor of DbMnager2"""
        self.conn = None  # type: Optional[Connection]
        self.db_name = db_name
        self.init_connection()
        self.init_db(db_name)

    def init_db(self, db_name: str) -> None:
        """Method to inizialize auxiliary database"""
        self.conn = sqlite3.connect(db_name)
        db_conn = self.conn.cursor()
        db_conn.execute('''CREATE TABLE IF NOT EXISTS AddressProcessed (
                        Address VARCHAR(128) PRIMARY KEY,
                        Currency VARCHAR(4),
                        Status NUMERIC,
                        Inferred NUMERIC
                    )''')
        db_conn.execute('''CREATE TABLE IF NOT EXISTS AddressToProcess (
                        Address VARCHAR(128) PRIMARY KEY,
                        Currency VARCHAR(4),
                        Status NUMERIC,
                        Inferred NUMERIC
                    )''')
        self.conn.commit()
        self.conn.close()

    def init_connection(self) -> None:
        """Method to open the database"""
        self.conn = sqlite3.connect(self.db_name)

    def close_db(self) -> None:
        """Method to close the database"""
        self.conn.close()

    def save_changes(self) -> None:
        """Method to save changes into the database"""
        self.conn.commit()

    def save_and_close(self) -> None:
        """Method to save changes and close the database"""
        self.conn.commit()
        self.conn.close()

    def insert_processed(self, wallets: List[Wallet]) -> bool:
        """Method to insert into the database the wallet processed"""
        db_conn = self.conn.cursor()
        for wallet in wallets:
            try:
                db_conn.execute('''INSERT INTO AddressProcessed(Address,
                                   Currency, Status, Inferred)
                                   VALUES (?, ?, ?, ?)''',
                                (str(wallet.address), str(wallet.currency),
                                 wallet.status, wallet.inferred))
            except Error:
                traceback.print_exc()
                return False
        return True

    def insert_to_process(self, wallets: List[Wallet]) -> bool:
        """Method to insert into the database the wallet to process"""
        db_conn = self.conn.cursor()
        for wallet in wallets:
            try:
                db_conn.execute('''INSERT INTO AddressToProcess(Address,
                                   Currency, Status, Inferred)
                                   VALUES (?, ?, ?, ?)''',
                                (str(wallet.address), str(wallet.currency),
                                 wallet.status, wallet.inferred))
            except Error:
                traceback.print_exc()
                return False
        return True

    def wallets_processed(self) -> List[Wallet]:
        """Method to retrieve the wallet processed"""
        db_conn = self.conn.cursor()
        wallets = []
        try:
            db_conn.execute('''SELECT * FROM AddressProcessed''')
            for row in db_conn:
                wallets.append(Wallet(row[0], row[1], '', row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets

    def wallets_to_process(self) -> List[Wallet]:
        """Method to retrieve the wallet to process"""
        db_conn = self.conn.cursor()
        wallets = []
        try:
            db_conn.execute('''SELECT * FROM AddressToProcess''')
            for row in db_conn:
                wallets.append(Wallet(row[0], row[1], '', row[2], row[3]))
        except Error:
            traceback.print_exc()
        return wallets

    def remove_to_process_wallets(self, wallets: List[Wallet]) -> None:
        """Method to clear all wallet to process"""
        db_conn = self.conn.cursor()
        for wallet in wallets:
            try:
                db_conn.execute('''DELETE FROM AddressToProcess WHERE
                                   Address = (?)''', (wallet.address,))
            except Error:
                traceback.print_exc()
