from address_checkers.abs_address_checker import AbsAddressChecker
import requests
import json
from time import sleep


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
        r = ''
        while True:
            exception_raised = False
            try:
                r = requests.get(self.createURL(addr))
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = r.text
        try:
            jsonResp = json.loads(resp)
            return (len(jsonResp[EthAddressChecker.RESULT]) > 0)
        except ValueError:
            return False
        return True

    def address_valid(self, addr):
        '''Check if addr is a valid Ethereum address using web3'''
        return self.address_search(addr)
