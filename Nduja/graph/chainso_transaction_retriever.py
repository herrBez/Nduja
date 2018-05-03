"""Module of base class that use chain.so API"""
from typing import Dict, Optional, Set, Any, Tuple

from time import sleep
import logging

import json
import sys
from graph.abs_transaction_retriever import AbsTransactionRetriever
from requests import Response

from graph.abs_transaction_retriever import AbsTransactionRetriever
from utility.print_utility import escape_utf8
from utility.safe_requests import safe_requests_get


class ChainSoTransactionRetriever(AbsTransactionRetriever):
    """Base class of classes that use chain.so transaction API"""
    chain_so_input_transaction = 'https://chain.so/api/v2/get_tx_received/'
    chain_so_output_transaction = 'https://chain.so/api/v2/get_tx_spent/'
    chain_so_transaction_info = 'https://chain.so/api/v2/get_tx/'

    def __init__(self, currency: str) -> None:
        self._currency = currency
        self.chain_so_input_transaction = \
            ChainSoTransactionRetriever.chain_so_input_transaction + currency \
            + '/'
        self.chain_so_output_transaction = \
            ChainSoTransactionRetriever.chain_so_output_transaction + currency \
            + '/'
        self.chain_so_transaction_info = \
            ChainSoTransactionRetriever.chain_so_transaction_info + currency \
            + '/'

    def get_currency(self) -> str:
        return self._currency

    @staticmethod
    def manage_response(query: str, response: Optional[Response]) -> \
            Optional[Dict[str, Any]]:
        """Method that take a response and construct a dict from it"""
        resp = None  # type: Optional[Dict[str, Any]]
        if response is None:
            logging.warning("ChainSoTransactionRetriever %s failed", query)
        else:
            raw_response = response.text
            try:
                resp = json.loads(raw_response)
            except json.decoder.JSONDecodeError:
                print("Response is not a valid JSON")
                with open('invalid_json.txt', 'a') as the_file:
                    the_file.write(query + "\n")
                print(escape_utf8(response.text))
                sleep(1)
        return resp

    @staticmethod
    def retrieve_transaction(query: str, timestamp: int) -> Optional[Set[str]]:
        """Mathod that take a response and extract transactions"""
        response = safe_requests_get(query=query, token=None, timeout=30,
                                     jsoncheck=True)
        resp = ChainSoTransactionRetriever.manage_response(query, response)
        if resp is None:
            return None
        logging.debug("%s", query)
        try:
            txs = resp["data"]["txs"]  # type: Any
            txid_set = set(
                [str(t["txid"]) for t in txs if t["time"] < timestamp]) \
                # type: Set[str]
        except KeyError:
            logging.error("%s: query %s failed", __file__, query)
            txid_set = set([])

        sleep(1)
        return txid_set

    def get_input_output_addresses(self, address: str,
                                   timestamp: Optional[int] = None) \
            -> Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        timestamp = AbsTransactionRetriever.timestamp_class \
            if timestamp is None else timestamp

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        # TODO Decomment if input transaction are necessary
        # query_input = self.CHAIN_SO_INPUT_TRANSACTION + address
        in_txid_set = None #  type: Optional[Set[Any]]
        #  ChainSoTransactionRetriever. \
        #    retrieve_transaction(query_input, timestamp)

        query_output = self.chain_so_output_transaction + address
        out_txid_set =  ChainSoTransactionRetriever. \
            retrieve_transaction(query_output, timestamp)

        if in_txid_set is None and out_txid_set is None:
            return inputs_dict, outputs_dict, connected_dict
        elif in_txid_set is None:
            in_txid_set = set([])
        elif out_txid_set is None:
            out_txid_set = set([])

        txid_set = in_txid_set.union(out_txid_set)
        for txid in txid_set:
            transaction_query = self.chain_so_transaction_info + str(txid)
            response = safe_requests_get(query=transaction_query, token=None,
                                         timeout=30, jsoncheck=True)
            resp = ChainSoTransactionRetriever. \
                manage_response(transaction_query, response)
            if resp is None:
                return inputs_dict, outputs_dict, connected_dict

            out_addr = {}  # type: Dict[str, int]
            in_addr = {}  # type: Dict[str, int]

            tmp_inputs_list = []
            tmp_outputs_list = []

            try:
                for o in resp["data"]["outputs"]:
                    try:
                        e = o["address"]
                        tmp_outputs_list.append(e)
                        out_addr[e] = 1
                    except KeyError:
                        logging.error("Corrupted content in chain.so api:"
                                        + "One output address in transaction: "
                                        + str(txid)
                                        + " is not valid. Skip this output")
            except KeyError:
                logging.error("Corrupted content in chain.so api:"
                              + "One output address in transaction: "
                              + str(txid)
                              + " is not valid. Skip this output")
            try:
                for i in resp["data"]["inputs"]:
                    try:
                        e = i["address"]
                        tmp_inputs_list.append(e)
                        in_addr[e] = 1
                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One input address in transaction: "
                                      + str(txid)
                                      + " is not valid. Skip this input")
            except KeyError:
                logging.error("Corrupted content in bitcoin api:"
                              + "One input address in transaction: "
                              + str(txid)
                              + " is not valid. Skip this input")
            if set(tmp_outputs_list).intersection(set(tmp_inputs_list)):
                with open("suspect_transactions.txt", "a") as myfile:
                    myfile.write("===\n")
                    myfile.write(str(txid) + "\n")
                    myfile.write("===\n")

            if address in tmp_outputs_list:
                for inp in in_addr:
                    if inp in inputs_dict:
                        inputs_dict[inp] += 1
                    else:
                        inputs_dict[inp] = 1

            if address in tmp_inputs_list:
                for inp in out_addr:
                    if inp in outputs_dict:
                        outputs_dict[inp] += 1
                    else:
                        outputs_dict[inp] = 1

            if address in tmp_inputs_list:
                for inp in tmp_inputs_list:
                    if inp != address:
                        if inp in connected_dict:
                            connected_dict[inp] += 1
                        else:
                            connected_dict[inp] = 1
            sleep(1)
        return inputs_dict, outputs_dict, connected_dict
