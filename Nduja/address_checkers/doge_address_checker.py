import logging
from typing import List
from typing import Any

import json
import requests
from time import sleep
from address_checkers.abs_address_checker import AbsAddressChecker
from utility.safe_requests import safe_requests_get

class DogeAddressChecker(AbsAddressChecker):
    """Doge address checker"""

    CHAIN_SO = "https://chain.so/api/v2/is_address_valid/DOGE/"
    CHAIN_SO_TXS_NUM = "https://chain.so/api/v2/get_tx/DOGE/"
    STATUS = "status"
    SUCCESS = "success"
    DATA = "data"
    ISVALID = "is_valid"

    @staticmethod
    def address_search(address: str) -> bool:
        """Use chain.so API to check if an address is valid"""


        r = safe_requests_get(DogeAddressChecker.CHAIN_SO + address,
                              jsoncheck=True, max_retries=10)
        if r is None:
            logging.warning(address + " Keep the result because the API is" +
                                      "temporary not available")
            return True

        try:
            json_response = json.loads(r.text)
            if (json_response[DogeAddressChecker.STATUS] ==
                    DogeAddressChecker.SUCCESS):
                return (json_response[DogeAddressChecker.DATA]
                        [DogeAddressChecker.ISVALID])
            else:
                return False
        except ValueError:
            sleep(0.5)
            return False
        return True

    def address_valid(self, address: str) -> bool:
        return len(address) == 34 and address.startswith("D")

    def address_check(self, address: str) -> bool:
        """Check if a Doge address is valid"""
        if self.address_valid(address):
            return DogeAddressChecker.address_search(address)
        return False

    def get_status(self, address: str) -> int:
        r = None
        while True:
            exception_raised = False
            try:
                r = requests.get(DogeAddressChecker.CHAIN_SO_TXS_NUM + address)
                # WARNING: chain.so API give 5request/sec for free
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = r.text
        try:
            json_response = json.loads(resp)
            inputs = []  # type: List[Any]
            outputs = []  # type: List[Any]

            try:
                inputs = json_response["data"]["inputs"]
            except KeyError:
                pass

            try:
                outputs = json_response["data"]["outputs"]
            except KeyError:
                pass

            return 1 if len(inputs) > 0 or len(outputs) > 0 else 0
        except ValueError:
            return 0
