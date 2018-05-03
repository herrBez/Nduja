"""Module for parsing search results"""
from typing import List, Callable, Dict, Any

import json

from db.db_manager import DbManager
from address_checkers.abs_address_checker import AbsAddressChecker
from tqdm import tqdm


class Parser:
    """Parser class"""

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
        """Method to parsing result if passed as string"""
        return Parser.parse(json.loads(string))

    def parse_file(self, path: str) -> None:
        """Method to parsing result if passed as file"""
        return Parser.parse(json.load(open(path)))

    @staticmethod
    def parse(results: List[Dict[str, Any]]) -> None:
        """Method to parse search results"""
        for res in tqdm(results,
                        desc="Check Status",
                        leave=True):
            symbols = res[Parser.SYMBOLS]
            wallets = res[Parser.WALLETS]
            account_id = None
            Parser.dbManager.init_connection()
            for i in range(len(symbols)):
                sym = symbols[i]
                wal = wallets[i]
                checker = Parser.retrieve_checker(sym)
                if checker.address_valid(wal):
                    if account_id is None:
                        account_id = (Parser.dbManager.
                                      find_account(res[Parser.HOST],
                                                   res[Parser.USERNAME]))
                        if account_id == -1:
                            account_id = Parser.dbManager.insert_account_no_info(
                                res[Parser.HOST],
                                res[Parser.USERNAME])
                    if not Parser.dbManager.find_wallet(wal):
                        if checker.address_check(wal):
                            status = checker.get_status(wal)
                            (Parser.dbManager.
                             insert_wallet_with_account(wal, sym, status,
                                                        account_id,
                                                        res[Parser.URL]))
            Parser.dbManager.save_changes()

    @staticmethod
    def valid_wallets(wallets: List[str],
                      checker: AbsAddressChecker) -> List[str]:
        """Return a list of valid addresses from the list passed as argument"""
        valid_wallets = []
        for wallet in wallets:
            if checker.address_valid(wallet):
                valid_wallets.append(wallet)
        return valid_wallets

    @staticmethod
    def retrieve_checker(currency: str) -> AbsAddressChecker:
        """Retrieve the right checker given a currency"""
        if currency in Parser.CURRENCIES:
            return Parser.get_class('address_checkers.' +
                                    currency.lower() + "_address_checker." +
                                    currency.lower().title() +
                                    "AddressChecker")()
        return None

    @staticmethod
    def get_class(name) -> Callable:
        """Retrieve the class of the checker of a certain currency"""
        parts = name.split('.')
        module = ".".join(parts[:-1])
        mod = __import__(module)
        for comp in parts[1:]:
            mod = getattr(mod, comp)
        return mod
