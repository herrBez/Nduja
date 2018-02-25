from typing import List
from typing import Any

from address_checkers.abs_address_checker import AbsAddressChecker
import requests
import json
from time import sleep
from requests import Response
import logging

from utility.safe_requests import safe_requests_get
from web3 import Web3


class EthAddressChecker(AbsAddressChecker):
    """Ethereum address checker"""

    P1 = "https://api.etherscan.io/api?module=account&action=balance&address="
    P2 = "&tag=latest&apikey="
    token = []  # type: List[str]
    token_index = 0
    RESULT = "result"

    @staticmethod
    def get_next_token() -> str:
        token = EthAddressChecker.token[EthAddressChecker.token_index]
        EthAddressChecker.token_index = ((EthAddressChecker.token_index + 1) %
                                         len(EthAddressChecker.token))
        return token

    @staticmethod
    def set_token(token: List[str]):
        EthAddressChecker.token = token

    @staticmethod
    def create_url(address: str) -> str:
        url = (EthAddressChecker.P1 + address + EthAddressChecker.P2 +
               EthAddressChecker.get_next_token())
        return url

    @staticmethod
    def address_search(address: str) -> bool:
        r = Response()
        while True:
            exception_raised = False
            try:
                r = requests.get(EthAddressChecker.create_url(address))
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

    @staticmethod
    def is_contract(address: str) -> bool:
        """This method takes as input an ethereum address and returns True
        if it is a contract address, False otherwise"""

        base_url = 'https://api.etherscan.io/api?'

        payload = {'module': 'contract',
                   'action': 'getabi',
                   'address': address,
                   'apikey':
                       EthAddressChecker.get_next_token()
                   }

        while True:
            exception_raised = False
            try:
                response = requests.get(base_url, params=payload)
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break

        resp = response.text
        json_resp = json.loads(resp)

        return json_resp["message"] == "OK"

    def address_valid(selfself, address: str) -> bool:
        return Web3.isAddress(address)

    def address_check(self, address: str) -> bool:
        """Check if addr is a valid Ethereum address using web3"""
        if self.address_valid(address):
            return EthAddressChecker.address_search(address) and \
                not EthAddressChecker.is_contract(address)
        else:
            return False

    def get_status(self, address: str) -> int:
        base_url = 'https://api.etherscan.io/api?'

        payload = {'module': 'account',
                   'action': 'txlist',
                   'address': address,
                   'apikey':
                       EthAddressChecker.get_next_token()
                   }
        r = safe_requests_get(query=base_url,
                              token=None,
                              jsoncheck=True,
                              params=payload)

        if r is None:
            logging.warning("The ethereum api is currently not available" +
                            " let's remain safe and returns 1")
            return 1

        else:
            resp = json.loads(r.text)

            txs = resp["result"]  # type: Any
            for t in txs: # if it has at least one element return True
                return 1
            return 0
