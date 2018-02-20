import os
import sqlite3
import traceback
from sqlite3 import Error
from sqlite3 import Cursor
from db.db_initializer import DbInitializer


def transfer_data(old_db: str, new_db: str, config_file: str) -> None:
    DbInitializer().init_db(new_db, config_file)
    old = sqlite3.connect(old_db)
    new = sqlite3.connect(new_db)
    c_new = new.cursor()
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
            new_id = None
            try:
                new_id = id_info[row[3]]
            except KeyError:
                print()
            c_new.execute('''INSERT INTO Account(Host, Username, Info)
                             VALUES (?,?,?)''', (row[1], row[2], new_id,))
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
    cold.execute("SELECT * FROM AccountRelated")
    for row in cold:
        try:
            c_new.execute('''INSERT INTO AccountRelated(Account1, Account2) 
                             VALUES (?,?)''',
                          (row[0], row[1],))
        except Error:
            traceback.print_exc()
    new.commit()
    new.close()
    old.close()
