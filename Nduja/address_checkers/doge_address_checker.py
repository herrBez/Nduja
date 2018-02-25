import json
import requests
from time import sleep
from address_checkers.abs_address_checker import AbsAddressChecker


class DogeAddressChecker(AbsAddressChecker):
    """Doge address checker"""

    CHAIN_SO = "https://chain.so/api/v2/is_address_valid/DOGE/"
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
                r = requests.get(DogeAddressChecker.CHAIN_SO + address)
                # WARNING: chain.so API give 5request/sec for free
            except requests.exceptions.ConnectionError:
                sleep(1)
                exception_raised = True
            if not exception_raised:
                break
        resp = r.text
        try:
            json_response = json.loads(resp)
            if (json_response[DogeAddressChecker.STATUS] ==
                    DogeAddressChecker.SUCCESS):
                return (json_response[DogeAddressChecker.DATA]
                        [DogeAddressChecker.ISVALID])
            else:
                return False
        except ValueError:
            return False
        return True

    def address_valid(self, address: str) -> bool:
        return len(address) == 34 and address.startswith("D")

    def address_check(self, address: str) -> bool:
        """Check if a Doge address is valid"""
        if self.address_valid(address):
            return DogeAddressChecker.address_search(address)
        return False
