import json
import logging
from hashlib import sha256
import requests
from address_checkers.abs_address_checker import AbsAddressChecker
from utility.safe_requests import safe_requests_get


class BtcAddressChecker(AbsAddressChecker):
    """Bitcoin address checker"""

    DIGITS58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    # Used for searching the address in the blockchain
    BITCOIN_INFO = "https://blockchain.info/rawaddr/"

    @staticmethod
    def decode_base58(bc: str, length: int) -> bytes:
        """Returns the base 58 econding of the wallet"""
        n = 0
        for char in bc:
            n = n * 58 + BtcAddressChecker.DIGITS58.index(char)
        return n.to_bytes(length, "big")

    def address_valid(self, bc):
        """Checks if the string passed could be a valid address for a bitcoin
        wallet"""
        if "I" in bc or "l" in bc or "O" in bc or "0" in bc:
            return False
        try:
            bcbytes = BtcAddressChecker.decode_base58(bc, 25)
            return bcbytes[-4:] == \
                sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
        except Exception:
            return False

    @staticmethod
    def address_search(address: str):
        """Checks if the bitcoin address exists"""
        query = BtcAddressChecker.BITCOIN_INFO + address
        r = safe_requests_get(query, jsoncheck=True, max_retries=10,
                              jsonerror_pause=4)
        if r is None:
            logging.warning(address + " Keep the result because the API is" +
                            "temporary not available")
            return True
        resp_txt = r.text
        try:
            json.loads(resp_txt)
            return True
        except ValueError:
            return False

    def address_check(self, address: str) -> bool:
        """Check if the bitcoin address is valid and exists"""
        if self.address_valid(address):
            return BtcAddressChecker.address_search(address)
        else:
            return False

    def get_status(self, address: str) -> int:
        query = BtcAddressChecker.BITCOIN_INFO + address
        r = safe_requests_get(query, jsoncheck=True, max_retries=10,
                              jsonerror_pause=4)
        if r is None:
            logging.warning(address + " Result 0 because the API is" +
                            "temporary not available")
            return 0
        resp_txt = r.text
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
