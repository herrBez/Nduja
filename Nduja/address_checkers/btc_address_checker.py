"""Module for checking Bitcoin addresses"""
import json
import logging
from hashlib import sha256
from address_checkers.abs_address_checker import AbsAddressChecker
from utility.safe_requests import safe_requests_get


class BtcAddressChecker(AbsAddressChecker):
    """Bitcoin address checker"""

    DIGITS58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    # Used for searching the address in the blockchain
    BITCOIN_INFO = "https://blockchain.info/rawaddr/"

    @staticmethod
    def decode_base58(bitcoin_address: str, length: int) -> bytes:
        """Returns the base 58 econding of the wallet"""
        num = 0
        for char in bitcoin_address:
            num = num * 58 + BtcAddressChecker.DIGITS58.index(char)
        return num.to_bytes(length, "big")

    def address_valid(self, address: str):
        """Checks if the string passed could be a valid address for a bitcoin
        wallet"""
        if "I" in address or "l" in address or "O" in address or "0" in address:
            return False
        try:
            bcbytes = BtcAddressChecker.decode_base58(address, 25)
            return bcbytes[-4:] == \
                sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
        except Exception:
            return False

    @staticmethod
    def address_search(address: str):
        """Checks if the bitcoin address exists"""
        query = BtcAddressChecker.BITCOIN_INFO + address
        response = safe_requests_get(query, jsoncheck=True, max_retries=10,
                                     jsonerror_pause=4)
        if response is None:
            warn = address + " Keep the result because the API is temporary " \
                             "not available"
            logging.warning(warn)
            return True
        resp_txt = response.text
        try:
            json.loads(resp_txt)
            return True
        except ValueError:
            return False

    def address_check(self, address: str) -> bool:
        """Check if the bitcoin address is valid and exists"""
        if self.address_valid(address):
            return BtcAddressChecker.address_search(address)
        return False

    def get_status(self, address: str) -> int:
        query = BtcAddressChecker.BITCOIN_INFO + address
        response = safe_requests_get(query, jsoncheck=True, max_retries=10,
                                     jsonerror_pause=4)
        if response is None:
            warn = address + " Result 0 because the API is temporary " \
                             "not available"
            logging.warning(warn)
            return 0
        resp_txt = response.text
        try:
            resp = json.loads(resp_txt)
            n_tx = resp["n_tx"]  # type: int
            return 1 if n_tx > 0 else 0
        except ValueError:
            return 0

# Usage example
# c = BtcAddressChecker()
# print(c.address_check("1AGNa15ZQXAZUgFiqJ3i7Z2DPU2J6hW62i"))
# print(c.address_check("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))
# print(c.address_check("16hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM"))
# print(c.address_check("6hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM"))
