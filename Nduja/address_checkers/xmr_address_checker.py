from address_checkers.abs_address_checker import AbsAddressChecker


class XmrAddressChecker(AbsAddressChecker):
    """Monero address checker"""

    def address_check(self, address: str) -> bool:
        """This function simply returns False because
        we have no way to know if address performed already transactions
        """
        return False

    def address_valid(self, address: str) -> bool:
        return address.startswith("4") and len(address) == 95
