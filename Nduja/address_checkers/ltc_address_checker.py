from typing import List
from typing import Any

import json
import requests
from time import sleep
from address_checkers.abs_address_checker import AbsAddressChecker


class LtcAddressChecker(AbsAddressChecker):
    """Litecoin Address Checker"""

    CHAIN_SO = "https://chain.so/api/v2/is_address_valid/LTC/"
    CHAIN_SO_TXS_NUM = "https://chain.so/api/v2/get_tx/LTC/"
    STATUS = "status"
    SUCCESS = "success"
    DATA = "data"
    ISVALID = "is_valid"

    @staticmethod
    def address_search(address: str) -> bool:
        """Use chain.so API to check if an address is valid"""
        r = None
        while True:
            exception_raised = False
            try:
                r = requests.get(LtcAddressChecker.CHAIN_SO + address)
                # WARNING: chain.so API give 5request/sec for free
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = r.text
        try:
            jsonResp = json.loads(resp)
            if (jsonResp[LtcAddressChecker.STATUS] ==
                    LtcAddressChecker.SUCCESS):
                return (jsonResp[LtcAddressChecker.DATA]
                        [LtcAddressChecker.ISVALID])
            else:
                return False
        except ValueError:
            return False
        return True

    def address_valid(self, address: str) -> bool:
        return ((address.startswith("L") or address.startswith("M")) and
                26 <= len(address) <= 36)  and \
                "I" not in address and "l" not in address and \
                "O" not in address and "0" not in address

    def address_check(self, address: str) -> bool:
        """Check if a litecoin address is valid"""
        if self.address_valid(address):
            return LtcAddressChecker.address_search(address)
        return False

    def get_status(self, address: str) -> int:
        r = None
        while True:
            exception_raised = False
            try:
                r = requests.get(LtcAddressChecker.CHAIN_SO_TXS_NUM + address)
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