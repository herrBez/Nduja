from address_checkers.abs_address_checker import AbsAddressChecker


class XmrAddressChecker(AbsAddressChecker):
    def address_check(self, addr):
        return False

    def address_valid(self, addr):
        return (addr.startswith('4') and len(addr) == 95)
