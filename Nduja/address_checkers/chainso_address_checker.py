"""Module that gives abstract class for checking addresses using Chain.so API"""
from typing import Any, List

import logging
from time import sleep
import json
from abc import ABCMeta, abstractmethod

from address_checkers.abs_address_checker import AbsAddressChecker
from utility.safe_requests import safe_requests_get


class ChainSoAddressChecker(AbsAddressChecker):
    """Abstract base class for address checkers"""
    __metaclass__ = ABCMeta

    CHAIN_SO = "https://chain.so/api/v2/is_address_valid/"
    CHAIN_SO_TXS_RECEIVED_NUM = "https://chain.so/api/v2/get_tx_received/"
    CHAIN_SO_TXS_SPENT_NUM = "https://chain.so/api/v2/get_tx_spent/"
    STATUS = "status"
    SUCCESS = "success"
    DATA = "data"
    ISVALID = "is_valid"
    TXS = "txs"

    @abstractmethod
    def is_valid_address_url(self) -> str:
        """Abstract method that returns the URL for checking if an address
        is valid"""
        pass

    @abstractmethod
    def get_spent_txs_url(self) -> str:
        """Abstract method that returns the URL for retrieving spent
        transactions"""
        pass

    @abstractmethod
    def get_received_txs_url(self) -> str:
        """Abstract method that returns the URL for retrieving received
        transactions"""
        pass

    def address_search(self, address: str) -> bool:
        """Use chain.so API to check if an address is valid"""
        response = safe_requests_get(self.is_valid_address_url() + address,
                                     jsoncheck=True, max_retries=10,
                                     jsonerror_pause=4)
        if response is None:
            warn = address + " Keep the result because the API is temporary " \
                             "not available"
            logging.warning(warn)
            return True

        try:
            json_response = json.loads(response.text)
            if (json_response[ChainSoAddressChecker.STATUS] ==
                    ChainSoAddressChecker.SUCCESS):
                return (json_response[ChainSoAddressChecker.DATA][
                    ChainSoAddressChecker.ISVALID])
            return False
        except ValueError:
            sleep(0.5)
            return False

    def address_check(self, address: str) -> bool:
        """Check if a Doge address is valid"""
        if self.address_valid(address):
            return self.address_search(address)
        return False

    def get_status(self, address: str) -> int:
        query_spent = self.get_spent_txs_url() + address
        r_spent = safe_requests_get(query_spent, jsoncheck=True, max_retries=5,
                                    jsonerror_pause=7)
        query_received = self.get_received_txs_url() + address
        r_received = safe_requests_get(query_received, jsoncheck=True,
                                       max_retries=5, jsonerror_pause=7)
        if r_spent is None and r_received is None:
            warn = address + " Result 0 because the API is temporary " \
                             "not available"
            logging.warning(warn)
            return 0
        elif r_spent is None:
            logging.warning(address + " the API is temporary not available " +
                            query_spent)
        elif r_received is None:
            logging.warning(address + " the API is temporary not available " +
                            query_received)
        try:
            inputs = []  # type: List[Any]
            if r_spent is not None:
                resp_spent = r_spent.text
                json_response_spent = json.loads(resp_spent)
                try:
                    inputs = json_response_spent["data"]["txs"]
                except KeyError:
                    pass

            outputs = []  # type: List[Any]
            if r_received is not None:
                resp_received = r_received.text
                json_response_received = json.loads(resp_received)
                try:
                    outputs = \
                        json_response_received[ChainSoAddressChecker.DATA][
                            ChainSoAddressChecker.TXS]
                except KeyError:
                    pass

            return 1 if inputs or outputs else 0
        except ValueError:
            return 0
