import os
import sqlite3
import traceback
from sqlite3 import Error
from sqlite3 import Cursor
from db.db_initializer import DbInitializer


def transfer_data(oldDb : str, newDb : str) -> None:
    DbInitializer().init_db(newDb)
    old = sqlite3.connect(oldDb)
    new = sqlite3.connect(newDb)
    cold = old.cursor()
    cnew = new.cursor()
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
    cold.execute("SELECT * FROM AccountRelated")
    for row in cold:
        try:
            cnew.execute('''INSERT INTO AccountRelated(Account1, Account2) 
                            VALUES (?,?)''',
                         (row[0], row[1],))
        except Error:
            traceback.print_exc()
    new.commit()
    new.close()
    old.close()
