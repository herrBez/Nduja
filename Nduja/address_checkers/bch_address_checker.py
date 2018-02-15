import json
from hashlib import sha256
import requests
from address_checkers.abs_address_checker import AbsAddressChecker


class BchAddressChecker(AbsAddressChecker):
    """Bitcoin cash address checker"""
    # TODO this checker must be refined

    DIGITS58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    # Used for searching the address in the blockchain
    BCH_CHAIN = "https://bch-chain.api.btc.com/v3/address/"
    ERR_NO = "err_no"
    NO_ERRORS = 0
    DATA = "data"

    @staticmethod
    def decode_base58(bc: str, length: int) -> bytes:
        """Returns the base 58 econding of the wallet"""
        n = 0
        for char in bc:
            n = n * 58 + BchAddressChecker.DIGITS58.index(char)
        return n.to_bytes(length, "big")

    def address_valid(self, bc: str) -> bool:
        """Checks if the string passed could be a valid address for a bitcoin
        wallet"""
        try:
            bcbytes = BchAddressChecker.decode_base58(bc, 25)
            return bcbytes[-4:] == \
                sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
        except Exception:
            return False

    @staticmethod
    def address_search(address: str) -> bool:
        """Checks if the bitcoin address exists"""
        r = requests.get(BchAddressChecker.BCH_CHAIN + address)
        resp = r.text
        try:
            json_resp = json.loads(resp)
            return ((json_resp[BchAddressChecker.ERR_NO] ==
                     BchAddressChecker.NO_ERRORS) and
                    (json_resp[BchAddressChecker.DATA]
                     is not None))
        except ValueError:
            return False

    def address_check(self, address: str) -> bool:
        """Check if the bitcoin address is valid and exists"""
        if address.startswith("bitcoincash:"):
            return True
        elif self.address_valid(address):
            return BchAddressChecker.address_search(address)
        else:
            return True
