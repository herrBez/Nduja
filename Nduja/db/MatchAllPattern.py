import json
import sqlite3
import traceback

from address_checkers import xmr_address_checker
from address_checkers.btc_address_checker import BtcAddressChecker
from address_checkers.eth_address_checker import EthAddressChecker
from address_checkers.xmr_address_checker import XmrAddressChecker
from db.db_initializer import DbInitializer
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from utility.pattern import Pattern
from utility.safe_requests import safe_requests_get
from wallet_collectors.abs_wallet_collector import flatten
from address_checkers.ltc_address_checker import LtcAddressChecker
from sqlite3 import Cursor



def insert_wallet(c, address: str, currency: str,
                  status: int,
                  inferred: bool = False) -> bool:
    int_inferred = 1 if inferred else 0  # type: int
    try:
        c.execute('''INSERT INTO Wallet(Address, Currency, Status, Inferred)
                         VALUES (?,?,?,?)''',
                  (str(address), str(currency), status,
                   int_inferred,))

    except sqlite3.Error:
        #traceback.print_exc()
        return False
    return True

def insert_account_wallet(c: Cursor,
                          account: int,
                          wallet: str,
                          url: str) -> int:
    try:
        c.execute('''INSERT INTO AccountWallet(Account, Wallet, RawURL)
            VALUES (?,?,?)''', (account, wallet, url,))
    except sqlite3.Error:
        traceback.print_exc()
        return -1
    c.execute('SELECT max(_id) FROM AccountWallet')
    max_id = c.fetchone()[0]
    return max_id


def match_all_pattern(format_file, db_name, config_file_path):
    DbManager.set_config_file(format_file)
    DbManager.set_db_file_name(db_name)

    with open(config_file_path, "r") as config_file:
        EthAddressChecker.set_token(json.loads(config_file.read())["tokens"]["etherscan"])

    format_object = json.loads(open(format_file).read())
    patterns = [Pattern(f) for f in format_object]

    mydb = sqlite3.connect(db_name)
    mydbcursor = mydb.cursor()

    mydbcursor.execute('''SELECT Address FROM Wallet''')
    wallet_list = set([r[0] for r in mydbcursor.fetchall()])

    mydbcursor.execute('''SELECT DISTINCT a._id, aw.RawUrl 
    FROM Account as a, AccountWallet as aw, Wallet as w 
    WHERE a._id = aw.Account AND w.Address = aw.Wallet AND w.Currency="DOGE"''')

    raw_result = mydbcursor.fetchall()

    account_ids = [r[0] for r in raw_result]
    raw_urls = [r[1] for r in raw_result]

    for i in range(len(raw_urls)):
        print("Processing " + str(i) + " of " + str(len(raw_urls)-1))
        response = safe_requests_get(raw_urls[i])
        if response is not None:
            match_list = \
                flatten(
                    [x.match(response.text) for x in patterns]
                )

            # A match was found
            if len(match_list) > 0:
                match_list = list(set(match_list))
                tmp_list = list(zip(*match_list))
                symbol_list = list(tmp_list[0])
                wallet_list = list(tmp_list[1])

                for j in range(len(symbol_list)):
                    s = symbol_list[j]
                    w = wallet_list[j]
                    if w in raw_result:
                        continue
                    if s != "DOGE":
                        continue
                    checker = Parser.retrieve_checker(s)

                    if checker.address_valid(w):
                        status = checker.get_status(w)
                        if checker.address_check(w):


                            try:
                                # if success = false --> it was already inserted
                                success = insert_wallet(mydbcursor,
                                                        w,
                                                        s,
                                                        status,
                                                        False)
                                if not success:
                                    insert_account_wallet(mydbcursor,
                                                          account_ids[i],
                                                          w,
                                                          raw_urls[i])


                            except Exception:
                                traceback.print_exc()

    mydb.commit()

    mydb.close()


if __name__ == "__main__":
    match_all_pattern("../format.json", "../DogeCoinAll.db", "../conf.json")
