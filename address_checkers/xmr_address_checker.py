from address_checkers.abs_address_checker import AbsAddressChecker


class XmrAddressChecker(AbsAddressChecker):
    """Monero address checker"""

    def address_check(self, address):
        """This function simply returns False because
        we have no way to know if address performed already transactions
        """
        return False

    def address_valid(self, address):
        return address.startswith("4") and len(address) == 95
