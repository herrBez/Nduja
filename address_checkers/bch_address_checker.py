import json
import requests
from hashlib import sha256
from address_checkers.abs_address_checker import AbsAddressChecker


class BchAddressChecker(AbsAddressChecker):
    '''WARNING this checker must be refined'''
    DIGITS58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    # Used for searching the address in the blockchain
    BCHCHAIN = 'https://bch-chain.api.btc.com/v3/address/'
    ERRNO = "err_no"
    NOERRORS = 0
    DATA = "data"

    def decode_base58(self, bc, length):
        '''Returns the base 58 econding of the wallet'''
        n = 0
        for char in bc:
            n = n * 58 + BchAddressChecker.DIGITS58.index(char)
        return n.to_bytes(length, 'big')

    def address_valid(self, bc):
        '''Checks if the string passed could be a valid address for a bitcoin
        wallet'''
        try:
            bcbytes = self.decode_base58(bc, 25)
            return bcbytes[-4:] == \
                sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
        except Exception:
            return False

    def address_search(self, addr):
        '''Checks if the bitcoin address exists'''
        r = requests.get(BchAddressChecker.BCHCHAIN + addr)
        resp = r.text
        try:
            jresp = json.loads(resp)
            return ((jresp[BchAddressChecker.ERRNO] ==
                     BchAddressChecker.NOERRORS) and
                    (jresp[BchAddressChecker.DATA]
                     is not None))
        except ValueError:
            return False

    def address_check(self, addr):
        '''Check if the bitcoin address is valid and exists'''
        if (addr.startswith('bitcoincash:')):
            return True
        elif (self.address_valid(addr)):
            return self.address_search(addr)
        else:
            return True
