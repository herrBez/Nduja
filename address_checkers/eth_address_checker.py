from web3 import Web3
from address_checkers.abs_address_checker import AbsAddressChecker
import requests
import json


class EthAddressChecker(AbsAddressChecker):
    P1 = 'https://api.etherscan.io/api?module=account&action=balance&address='
    P2 = '&tag=latest&apikey='
    token = None
    token_index = 0
    RESULT = "result"

    def setToken(token):
        EthAddressChecker.token = token

    def createURL(self, addr):
        url = (EthAddressChecker.P1 + addr + EthAddressChecker.P2 +
               (EthAddressChecker.token[EthAddressChecker.token_index]))
        EthAddressChecker.token_index = ((EthAddressChecker.token_index + 1) %
                                         len(EthAddressChecker.token))
        return url

    def address_check(self, addr):
        return False

    def address_search(self, addr):
        r = requests.get(self.createURL(addr))
        resp = r.text
        try:
            jsonResp = json.loads(resp)
            return (len(jsonResp[EthAddressChecker.RESULT]) > 0)
        except ValueError:
            return False
        return True

    def address_valid(self, addr):
        '''Check if addr is a valid Ethereum address using web3'''
        if (Web3.isAddress(addr)):
            return self.address_search(addr)
        return False
