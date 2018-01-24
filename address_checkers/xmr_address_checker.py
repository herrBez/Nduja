from abs_address_checker import AbsAddressChecker


class XmrAddressChecker(AbsAddressChecker):
    def address_check(self, addr):
        '''Check is an Ethereum address is valid using web3'''
        return (addr.startswith('4') and len(addr) == 95)
