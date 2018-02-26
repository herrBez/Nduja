from address_checkers.chainso_address_checker import ChainSoAddressChecker


class DogeAddressChecker(ChainSoAddressChecker):
    """Doge address checker"""

    CHAIN_SO = ChainSoAddressChecker.CHAIN_SO + "DOGE/"
    CHAIN_SO_TXS_RECEIVED_NUM = \
        ChainSoAddressChecker.CHAIN_SO_TXS_RECEIVED_NUM + "DOGE/"
    CHAIN_SO_TXS_SPENT_NUM = \
        ChainSoAddressChecker.CHAIN_SO_TXS_SPENT_NUM + "DOGE/"

    def is_valid_address_url(self) -> str:
        return DogeAddressChecker.CHAIN_SO

    def get_spent_txs_url(self) -> str:
        return DogeAddressChecker.CHAIN_SO_TXS_SPENT_NUM

    def get_received_txs_url(self) -> str:
        return DogeAddressChecker.CHAIN_SO_TXS_RECEIVED_NUM

    def address_valid(self, address: str) -> bool:
        return len(address) == 34 and address.startswith("D") and \
                "I" not in address and "l" not in address and \
                "O" not in address and "0" not in address

    def address_check(self, address: str) -> bool:
        """Check if a Doge address is valid"""
        if self.address_valid(address):
            return self.address_search(address)
        return False
