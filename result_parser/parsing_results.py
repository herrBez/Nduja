import json
from db.db_manager import DbManager


class Parser:
    '''
    exec(open("./parsing_results.py").read())
    Parser().parse('/home/zanna/Desktop/search-result.json')
    '''
    dbManager = None

    def __init__(self):
        Parser.dbManager = DbManager.getInstance()

    def parse(self, path):
        results = json.load(open(path))
        for res in results["results"]:
            checker = self.retrieveChecker(res["symbol"])
            valid = self.validWallets(res["wallet"], checker)
            if (len(valid) > 0):
                accountId = Parser.dbManager.findAccount(res["host"],
                                                         res["username"])
                if (accountId == -1):
                    accountId = Parser.dbManager.insertAccountNoInfo(
                        res["host"],
                        res["username"])
                for w in valid:
                    if (not(Parser.dbManager.findWallet(w))):
                        status = 0
                        if (checker.address_check(w)):
                            status = 1
                        if (res["symbol"] in ['XMR', 'BCH', 'ETH', 'ETC']):
                            status = 0
                        (Parser.dbManager.
                         insertWalletWithAccount(w, res["symbol"],
                                                 status, accountId,
                                                 res["known_raw_url"]))

    def validWallets(self, wallets, checker):
        validWallets = []
        for wallet in wallets:
            if (checker.address_valid(wallet)):
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
