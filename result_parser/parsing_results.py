import json
from db.db_manager import DbManager


class Parser:
    dbManager = None
    SYMBOLS = "symbol"
    WALLETS = "wallet_list"
    RESULTS = "results"
    HOST = "hostname"
    USERNAME = "username"
    URL = "known_raw_url"
    NOT_SURE_CHECK = ['XMR', 'BCH', 'ETH', 'ETC']
    CURRENCIES = ['BTC', 'BCH', 'DOGE', 'XMR', 'LTC']

    def __init__(self):
        Parser.dbManager = DbManager.getInstance()

    def parseString(self, string):
        return self.parse(json.loads(string))

    def parseFile(self, path):
        return self.parse(json.load(open(path)))

    def parse(self, results):
        for res in results[Parser.RESULTS]:
            symbols = res[Parser.SYMBOLS]
            wallets = res[Parser.WALLETS]
            accountId = None
            for i in range(0, len(symbols)):
                s = symbols[i]
                w = wallets[i]
                checker = self.retrieveChecker(s)
                if (checker.address_valid(w)):
                    if accountId is None:
                        accountId = (Parser.dbManager.
                                     findAccount(res[Parser.HOST],
                                                 res[Parser.USERNAME]))
                        if (accountId == -1):
                            accountId = Parser.dbManager.insertAccountNoInfo(
                                res[Parser.HOST],
                                res[Parser.USERNAME])
                    if (not(Parser.dbManager.findWallet(w))):
                        status = 0
                        if (checker.address_check(w)):
                            status = 1
                        if (s in Parser.NOT_SURE_CHECK):
                                status = 0
                        (Parser.dbManager.
                         insertWalletWithAccount(w, s, status, accountId,
                                                 res[Parser.URL]))

    def validWallets(self, wallets, checker):
        validWallets = []
        for wallet in wallets:
            if (checker.address_valid(wallet)):
                validWallets.append(wallet)
        return validWallets

    def retrieveChecker(self, currency):
        if (currency in Parser.CURRENCIES):
            return self.getClass('address_checkers.' +
                                 currency.lower() + "_address_checker." +
                                 currency.lower().title() + "AddressChecker")()
        elif (currency in ['ETH', 'ETC']):
            return self.getClass('address_checkers.ethereum_address_checker.' +
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
