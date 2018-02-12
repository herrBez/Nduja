from address_checkers.abs_address_checker import AbsAddressChecker
import requests
import json
from time import sleep
from requests import Response

class EthAddressChecker(AbsAddressChecker):
    """Ethereum address checker"""

    P1 = "https://api.etherscan.io/api?module=account&action=balance&address="
    P2 = "&tag=latest&apikey="
    token = None
    token_index = 0
    RESULT = "result"

    @staticmethod
    def setToken(token: str):
        EthAddressChecker.token = token

    def createURL(self, address: str) -> str:
        url = (EthAddressChecker.P1 + address + EthAddressChecker.P2 +
               (EthAddressChecker.token[EthAddressChecker.token_index]))
        EthAddressChecker.token_index = ((EthAddressChecker.token_index + 1) %
                                         len(EthAddressChecker.token))
        return url

    def address_check(self, address: str) -> bool:
        return False

    def address_search(self, address: str) -> bool:
        r = Response()
        while True:
            exception_raised = False
            try:
                r = requests.get(self.createURL(address))
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = r.text
        try:
            json_resp = json.loads(resp)
            return len(json_resp[EthAddressChecker.RESULT]) > 0
        except ValueError:
            return False
        return True

    def address_valid(self, address: str) -> bool:
        """Check if addr is a valid Ethereum address using web3"""
        return self.address_search(address)