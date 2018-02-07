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
        Parser.dbManager = DbManager.getInstance()

    def parseString(self, string: str) -> None:
        return self.parse(json.loads(string))

    def parseFile(self, path: str) -> None:
        return self.parse(json.load(open(path)))

    def parse(self, results: Dict[str, Any]) -> None:
        for res in results[Parser.RESULTS]:
            symbols = res[Parser.SYMBOLS]
            wallets = res[Parser.WALLETS]
            account_id = None
            Parser.dbManager.initConnection()
            for i in range(0, len(symbols)):
                s = symbols[i]
                w = wallets[i]
                checker = self.retrieveChecker(s)
                if checker.address_valid(w):
                    if account_id is None:
                        account_id = (Parser.dbManager.
                                     findAccount(res[Parser.HOST],
                                                 res[Parser.USERNAME]))
                        if account_id == -1:
                            account_id = Parser.dbManager.insertAccountNoInfo(
                                res[Parser.HOST],
                                res[Parser.USERNAME])
                    if not Parser.dbManager.findWallet(w):
                        status = 0
                        if checker.address_check(w):
                            status = 1
                        if s in Parser.NOT_SURE_CHECK:
                                status = 0
                        (Parser.dbManager.
                         insertWalletWithAccount(w, s, status, account_id,
                                                 res[Parser.URL]))
            Parser.dbManager.saveChanges()

    def validWallets(self, wallets: List[str],
                     checker: AbsAddressChecker) -> List[str]:
        valid_wallets = []
        for wallet in wallets:
            if checker.address_valid(wallet):
                valid_wallets.append(wallet)
        return valid_wallets

    def retrieveChecker(self, currency: str) -> AbsAddressChecker:
        if currency in Parser.CURRENCIES:
            return self.getClass('address_checkers.' +
                                 currency.lower() + "_address_checker." +
                                 currency.lower().title() + "AddressChecker")()
        else:
            return None

    def getClass(self, name) -> Callable:
        parts = name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
