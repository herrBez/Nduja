from typing import List
from typing import Any

import logging
import json
import requests
from time import sleep
from address_checkers.abs_address_checker import AbsAddressChecker
from address_checkers.chainso_address_checker import ChainSoAddressChecker
from utility.safe_requests import safe_requests_get


class LtcAddressChecker(ChainSoAddressChecker):
    """Litecoin Address Checker"""

    CHAIN_SO = ChainSoAddressChecker.CHAIN_SO + "LTC/"
    CHAIN_SO_TXS_RECEIVED_NUM = \
        ChainSoAddressChecker.CHAIN_SO_TXS_RECEIVED_NUM + "LTC/"
    CHAIN_SO_TXS_SPENT_NUM = \
        ChainSoAddressChecker.CHAIN_SO_TXS_SPENT_NUM + "LTC/"

    def is_valid_address_url(self) -> str:
        return LtcAddressChecker.CHAIN_SO

    def get_spent_txs_url(self) -> str:
        return LtcAddressChecker.CHAIN_SO_TXS_SPENT_NUM

    def get_received_txs_url(self) -> str:
        return LtcAddressChecker.CHAIN_SO_TXS_RECEIVED_NUM

    def address_valid(self, address: str) -> bool:
        return ((address.startswith("L") or address.startswith("M")) and
                26 <= len(address) <= 36) and \
                "I" not in address and "l" not in address and \
                "O" not in address and "0" not in address

    def address_check(self, address: str) -> bool:
        """Check if a litecoin address is valid"""
        if self.address_valid(address):
            return self.address_search(address)
        return False
