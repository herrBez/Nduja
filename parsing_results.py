import json
from db_manager import DbManager


class Parser:
    dbManager = None

    def __init__(self):
        Parser.dbManager = DbManager()

    def parse(self, path):
        results = json.load(open(path))
        for res in results["results"]:
            checker = self.retrieveChecker(res["symbol"])
            valid = self.validWallets(res["wallets"], checker)
            if (len(valid) > 0):
                accountId = Parser.dbManager.findAccount(res["username"],
                                                         res["host"])
                if (accountId == -1):
                    accountId = Parser.dbManager.insertAccountNoInfo()
                for w in valid:
                    if (not(Parser.dbManager.findWallet(w))):
                        used = 'OK'
                        if (res["symbol"] in ['XMR', 'BCH', 'ETH', 'ETC']):
                            used = 'NA'
                        Parser.insertWalletWithAccount(w, res["symbol"],
                                                       used,
                                                       accountId,
                                                       res["pathToFile"])

    def validWallets(self, wallets, checker):
        validWallets = []
        for wallet in wallets:
            if (checker._address_check(wallet)):
                validWallets.append(wallet)
        return validWallets

    def retrieveChecker(self, currency):
        CURRENCIES = ['BTC', 'BCH', 'DOGE', 'XMR', 'LTC']
        if (currency in CURRENCIES):
            return self.getClass('address_checkers.' +
                                 currency.lower() + "_address_checker." +
                                 currency.lower().title() + "AddressChecker")()
        elif (currency in ['ETH', 'ETC']):
            return self.getClass('address_checkers.' +
                                 currency.lower() + "_address_checker." +
                                 "EthereumAddressChecker")()
        else:
            return None

    def getClass(self, name):
        parts = name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
