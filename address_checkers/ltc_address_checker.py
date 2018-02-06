import json
import requests
from time import sleep
from address_checkers.abs_address_checker import AbsAddressChecker


class LtcAddressChecker(AbsAddressChecker):
    """Litecoin Address Checker"""

    CHAINSO = "https://chain.so/api/v2/is_address_valid/LTC/"
    STATUS = "status"
    SUCCESS = "success"
    DATA = "data"
    ISVALID = "is_valid"

    def address_search(self, addr):
        """Use chain.so API to check if an address is valid"""
        r = ""
        while True:
            exception_raised = False
            try:
                r = requests.get(LtcAddressChecker.CHAINSO + addr)
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

    def address_valid(self, address):
        return ((address.startswith("L") or address.startswith("M")) and
                26 <= len(address) <= 36)

    def address_check(self, address):
        """Check if a litecoin address is valid"""
        if self.address_valid(address):
            return self.address_search(address)
        return False
