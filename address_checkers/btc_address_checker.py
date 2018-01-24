import json
import requests
from hashlib import sha256
from address_checkers.abs_address_checker import AbsAddressChecker


class BtcAddressChecker(AbsAddressChecker):
    DIGITS58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    # Used for searching the address in the blockchain
    BITCOININFO = 'https://blockchain.info/rawaddr/'

    def decode_base58(self, bc, length):
        '''Returns the base 58 econding of the wallet'''
        n = 0
        for char in bc:
            n = n * 58 + BtcAddressChecker.DIGITS58.index(char)
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
        r = requests.get(BtcAddressChecker.BITCOININFO + addr)
        resp = r.text
        try:
            json.loads(resp)
        except ValueError:
            return False
        return True

    def address_check(self, addr):
        '''Check if the bitcoin address is valid and exists'''
        if (self.address_valid(addr)):
            return self.address_search(addr)
        else:
            return False

# Usage example
# c = BtcAddressChecker()
# print(c.address_check('1AGNa15ZQXAZUgFiqJ3i7Z2DPU2J6hW62i'))
# print(c.address_check("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))
# print(c.address_check('16hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
# print(c.address_check('6hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
