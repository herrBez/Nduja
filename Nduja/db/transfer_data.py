import json
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
    c_old = old.cursor()
    id_info = {}

    c_old.execute("SELECT * FROM Information")
    for row in c_old:
        c_new.execute('''INSERT INTO Information(Name, Website, Email, Json)
                         VALUES (?,?,?,?)''', (row[1], row[2], row[3], row[4],))
        c_new.execute('SELECT max(_id) FROM Information')
        id_info[row[0]] = c_new.fetchone()[0]
    new.commit()
    c_old.execute("SELECT * FROM Account")
    id_account = {}
    for row in c_old:
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
    c_old.execute("SELECT * FROM AccountWallet")
    for row in c_old:
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
    c_old.execute("SELECT * FROM Wallet")
    for row in c_old:
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
    c_old.execute("SELECT * FROM AccountRelated")
    for row in c_old:
        try:
            c_new.execute('''INSERT INTO AccountRelated(Account1, Account2) 
                             VALUES (?,?)''',
                          (row[0], row[1],))
        except Error:
            traceback.print_exc()
    new.commit()
    new.close()
    old.close()




def transfer_data2(old_db: str, new_db: str) -> None:
    old = sqlite3.connect(old_db)
    new = sqlite3.connect(new_db)
    c_new = new.cursor()
    c_old = old.cursor()
    c_old.execute('''SELECT _id, Host, Username, Info FROM Account''')

    raw_result = c_old.fetchall()

    old_account_to_new_map = {}

    for row in raw_result:
        old_account_id = row[0]
        old_host = row[1]
        old_username = row[2]
        old_info = row[3]
        c_new.execute('''SELECT * 
        FROM Account 
        WHERE host=(?) AND username=(?)''', (old_host, old_username, ))
        res = c_new.fetchall()

        if len(res) == 0:  # the account does not exist in the new db
            if old_info is not None:
                c_old.execute('''SELECT * FROM Information WHERE _id=(?)''',
                              (old_info,))
                info_object = c_old.fetchone()

                c_new.execute('''INSERT INTO
                Information(Name, Website, Email, Json) VALUES 
                (?,?,?,?)''', info_object[1:])

                c_new.execute('''SELECT max(_id) FROM Information''')
                max_id = c_new.fetchone()[0]


            c_new.execute('''INSERT INTO Account(Host, Username, Info)
            VALUES (?, ?, ?)''', (old_host, old_username, max_id))

            c_new.execute('''SELECT max(_id) FROM Account''')
            new_account_id = c_new.fetchone()[0]

            old_account_to_new_map[old_account_id] = new_account_id





        else:  # the account exist in the new db
            new_account_id = res[0][0]
            old_account_to_new_map[old_account_id] = new_account_id

            if old_info is not None:
                # info exists in old db

                new_host = res[0][1]
                new_username = res[0][2]
                new_info = res[0][3]
                if new_info is not None:
                    # both are present in the db
                    c_old.execute('''SELECT * FROM Information WHERE _id=(?)''',
                                  (old_info,))
                    c_new.execute('''SELECT * FROM Information WHERE _id=(?)''',
                                  (new_info,))

                    old_info_object = c_old.fetchone()
                    new_info_object = c_new.fetchone()

                    old_emails = old_info_object[3].split(",")
                    new_email = new_info_object[3].split(",")
                    emails = list(set(old_emails + new_email))

                    old_website = old_info_object[2].split(",")
                    new_website = new_info_object[2].split(",")
                    websites = list(set(old_website + new_website))

                    my_json = []
                    old_json = old_info_object[4]
                    new_json = new_info_object[4]
                    my_json.append(old_json)
                    if old_json != new_json:
                        my_json.append(new_json)

                    c_new.execute('''UPDATE Information set 
                    Website=(?), Email=(?), Json=(?) WHERE
                    _id = (?)''', ((','.join(websites) if len(websites) > 0
                                                                      else ''),
                                   ','.join(emails) if len(emails) > 0 else '',
                                   str(my_json),
                                   new_account_id
                                   ))
    print(old_account_to_new_map)
    c_old.execute('''SELECT * FROM AccountWallet''')
    raw_result = c_old.fetchall()
    for row in raw_result:
        old_account = row[1]
        old_wallet = row[2]
        old_raw_url = row[3]

        new_account = old_account_to_new_map[old_account]

        c_new.execute('''SELECT * FROM AccountWallet WHERE Account = (?) 
        AND Wallet = (?)''', (new_account, old_wallet))

        res = c_new.fetchall()
        if len(res) == 0:  # the AccountWallet is not present
            c_new.execute('''SELECT * FROM Wallet WHERE Address=(?)''',
                          (old_wallet,))
            wallet_obj = c_new.fetchall()
            if len(wallet_obj) == 0:  # Wallet does not exist in new db
                c_old.execute('''SELECT * FROM Wallet WHERE Address=(?)''',
                              (old_wallet, ))
                res = c_old.fetchone()
                try:
                    c_new.execute('''INSERT INTO Wallet(Address,Currency, Status,
                    Inferred) VALUES (?, ?, ?, ?)''', res)
                except sqlite3.IntegrityError:
                    pass
            c_new.execute('''INSERT INTO 
            AccountWallet(Account,Wallet,RawUrl) VALUES
            (?,?,?)''', (new_account, old_wallet, old_raw_url,))

        else:  # Wallet exists in new db
            new_raw_url = [res[0][3].strip()]
            if new_raw_url[0] != old_raw_url.strip(): # check the raw url
                new_raw_url.append(old_raw_url.strip())
                c_new.execute('''UPDATE AccountWallet set RawUrl=(?)
                WHERE _id=(?)''', (','.join(new_raw_url), res[0][0], ))

    try:
        c_old.execute("SELECT * FROM AccountRelated")
        for row in c_old:
            try:
                c_new.execute('''INSERT INTO AccountRelated(Account1, Account2) 
                                 VALUES (?,?)''',
                              (old_account_to_new_map[row[0]],
                               old_account_to_new_map[row[1]]))
            except sqlite3.IntegrityError:
                pass
    except sqlite3.Error:
        pass

    new.commit()
    new.close()
    old.close()


import sys

if __name__ == "__main__":
    transfer_data2(sys.argv[1], sys.argv[2])