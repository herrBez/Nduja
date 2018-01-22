import requests
import json
from hashlib import sha256


digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
bitcoininfo = 'https://blockchain.info/rawaddr/'


def decode_base58(bc, length):
    '''Returns the base 58 econding of the wallet'''
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')


def check_bc(bc):
    '''Checks if the string passed could be a valid address for a bitcoin
    wallet'''
    try:
        bcbytes = decode_base58(bc, 25)
        return bcbytes[-4:] == \
            sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
    except Exception:
        return False


def address_search(addr):
    '''Checks if the bitcoin address exists'''
    r = requests.get(bitcoininfo + addr)
    resp = r.text
    try:
        json.loads(resp)
    except ValueError:
        return False
    return True


def address_check(addr):
    '''Check if the bitcoin address is valid and exists'''
    if (check_bc(addr)):
        return address_search(addr)
    else:
        return False


print(address_check('1AGNa15ZQXAZUgFiqJ3i7Z2DPU2J6hW62i'))
print(address_check("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))
print(address_check('16hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
print(address_check('6hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
