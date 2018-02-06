from address_checkers.abs_address_checker import AbsAddressChecker
import requests
import json
from time import sleep


class EthAddressChecker(AbsAddressChecker):

    @staticmethod
    def setToken(token): ...

    def createURL(self, address: str) -> str: ...

    def address_check(self, address: str) -> bool: ...

    def address_search(self, address: str) -> bool: ...

    def address_valid(self, address : str) -> bool: ...