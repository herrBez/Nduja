from web3 import Web3
from abs_address_checker import AbsAddressChecker


class EthereumAddressChecker(AbsAddressChecker):
    def address_check(self, addr):
        '''Check if addr is a valid Ethereum address using web3'''
        return Web3.isAddress(addr)