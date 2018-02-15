import json
from db.db_manager import DbManager
from address_checkers.abs_address_checker import AbsAddressChecker
from typing import List, Callable, Dict, Any


class Parser:
    dbManager = None
    SYMBOLS = "symbol"
    WALLETS = "wallet_list"
    RESULTS = "results"
    HOST = "hostname"
    USERNAME = "username"
    URL = "known_raw_url"
    NOT_SURE_CHECK = ['XMR', 'BCH']
    CURRENCIES = ['BTC', 'BCH', 'DOGE', 'XMR', 'LTC', 'ETH']

    def __init__(self) -> None:
        Parser.dbManager = DbManager.get_instance()

    def parse_string(self, string: str) -> None:
        return Parser.parse(json.loads(string))

    def parse_file(self, path: str) -> None:
        return Parser.parse(json.load(open(path)))

    @staticmethod
    def parse(results: Dict[str, Any]) -> None:
        for res in results[Parser.RESULTS]:
            symbols = res[Parser.SYMBOLS]
            wallets = res[Parser.WALLETS]
            account_id = None
            Parser.dbManager.init_connection()
            for i in range(0, len(symbols)):
                s = symbols[i]
                w = wallets[i]
                checker = Parser.retrieve_checker(s)
                if checker.address_valid(w):
                    if account_id is None:
                        account_id = (Parser.dbManager.
                                      find_account(res[Parser.HOST],
                                                   res[Parser.USERNAME]))
                        if account_id == -1:
                            account_id = Parser.dbManager.insert_account_no_info(
                                res[Parser.HOST],
                                res[Parser.USERNAME])
                    if not Parser.dbManager.find_wallet(w):
                        status = 0
                        if checker.address_check(w):
                            status = 1
                        if s in Parser.NOT_SURE_CHECK:
                                status = 0
                        (Parser.dbManager.
                         insert_wallet_with_account(w, s, status, account_id,
                                                    res[Parser.URL]))
            Parser.dbManager.save_changes()

    @staticmethod
    def valid_wallets(wallets: List[str],
                      checker: AbsAddressChecker) -> List[str]:
        valid_wallets = []
        for wallet in wallets:
            if checker.address_valid(wallet):
                valid_wallets.append(wallet)
        return valid_wallets

    @staticmethod
    def retrieve_checker(currency: str) -> AbsAddressChecker:
        if currency in Parser.CURRENCIES:
            return Parser.get_class('address_checkers.' +
                                  currency.lower() + "_address_checker." +
                                  currency.lower().title() + "AddressChecker")()
        else:
            return None

    @staticmethod
    def get_class(name) -> Callable:
        parts = name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
