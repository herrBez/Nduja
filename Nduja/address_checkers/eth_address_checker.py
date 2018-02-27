"""Module for checking Ethereum addresses"""
from typing import List, Any

import logging
import json
from time import sleep

import requests
from requests import Response
from web3 import Web3

from address_checkers.abs_address_checker import AbsAddressChecker
from utility.safe_requests import safe_requests_get


class EthAddressChecker(AbsAddressChecker):
    """Ethereum address checker"""

    P1 = "https://api.etherscan.io/api?module=account&action=balance&address="
    P2 = "&tag=latest&apikey="
    token = []  # type: List[str]
    token_index = 0
    RESULT = "result"

    @staticmethod
    def get_next_token() -> str:
        """Return the next token that can be used to perform a request"""
        token = EthAddressChecker.token[EthAddressChecker.token_index]
        EthAddressChecker.token_index = ((EthAddressChecker.token_index + 1) %
                                         len(EthAddressChecker.token))
        return token

    @staticmethod
    def set_token(token: List[str]):
        """Set list of tokens that can be used to perform requests"""
        EthAddressChecker.token = token

    @staticmethod
    def create_url(address: str) -> str:
        """Create the request to be performed"""
        url = (EthAddressChecker.P1 + address + EthAddressChecker.P2 +
               EthAddressChecker.get_next_token())
        return url

    @staticmethod
    def address_search(address: str) -> bool:
        """Search the address in the blockchain to verify its validity"""
        response = Response()
        while True:
            exception_raised = False
            try:
                response = requests.get(EthAddressChecker.create_url(address))
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = response.text
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
                   'apikey': EthAddressChecker.get_next_token()}

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

    def address_valid(self, address: str) -> bool:
        """Check locally if the address has a valid format"""
        return Web3.isAddress(address)

    def address_check(self, address: str) -> bool:
        """Check if addr is a valid Ethereum address using web3"""
        if self.address_valid(address):
            return EthAddressChecker.address_search(address) and \
                not EthAddressChecker.is_contract(address)
        return False

    def get_status(self, address: str) -> int:
        """Return 1 if the address is used in some transaction, 0 otherwise"""
        base_url = 'https://api.etherscan.io/api?'

        payload = {'module': 'account',
                   'action': 'txlist',
                   'address': address,
                   'apikey': EthAddressChecker.get_next_token()}

        response = safe_requests_get(query=base_url,
                                     token=None,
                                     jsoncheck=True,
                                     params=payload)

        if response is None:
            logging.warning("The ethereum api is currently not available" +
                            " let's remain safe and returns 1")
            return 1

        resp = json.loads(response.text)

        txs = resp["result"]  # type: Any
        if txs:
            return 1
        return 0
