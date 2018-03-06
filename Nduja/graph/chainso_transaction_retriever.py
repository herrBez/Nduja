import logging
import time
from time import sleep
from typing import Dict, Optional, Set, Any, Tuple
import json

import logging

import sys
from graph.abs_transaction_retriever import AbsTransactionRetriever
from requests import Response
from utility.print_utility import escape_utf8
from utility.safe_requests import safe_requests_get


class ChainSoTransactionRetriever(AbsTransactionRetriever):

    CHAIN_SO_INPUT_TRANSACTION = 'https://chain.so/api/v2/get_tx_received/'
    CHAIN_SO_OUTPUT_TRANSACTION = 'https://chain.so/api/v2/get_tx_spent/'
    CHAIN_SO_TRANSACTION_INFO = 'https://chain.so/api/v2/get_tx/'

    def __init__(self, currency: str) -> None:
        self._currency = currency
        self.CHAIN_SO_INPUT_TRANSACTION = \
            ChainSoTransactionRetriever.CHAIN_SO_INPUT_TRANSACTION + currency \
            + '/'
        self.CHAIN_SO_OUTPUT_TRANSACTION = \
            ChainSoTransactionRetriever.CHAIN_SO_OUTPUT_TRANSACTION + currency \
            + '/'
        self.CHAIN_SO_TRANSACTION_INFO = \
            ChainSoTransactionRetriever.CHAIN_SO_TRANSACTION_INFO + currency \
            + '/'

    def get_currency(self) -> str:
        return self._currency

    @staticmethod
    def manage_response(query: str, response: Optional[Response]) -> \
            Optional[Dict[str, Any]]:
        resp = None  # type: Optional[Dict[str, Any]]
        if response is None:
            logging.warning("ChainSoTransactionRetriever " + query
                            + " failed")
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
        r = safe_requests_get(query=query, token=None, timeout=30,
                              jsoncheck=True)
        resp = ChainSoTransactionRetriever.manage_response(query, r)
        if resp is None:
            return None
        
        logging.info("%s", query)
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
            -> Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        timestamp = AbsTransactionRetriever.timestamp_class \
            if timestamp is None else timestamp

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        query_input = self.CHAIN_SO_INPUT_TRANSACTION + address
        in_txid_set = ChainSoTransactionRetriever. \
            retrieve_transaction(query_input, timestamp)

        # TODO Decomment if output transaction are necessary
        # query_output = self.CHAIN_SO_OUTPUT_TRANSACTION + address
        out_txid_set = None #  type: Optional[Set[Any]]
        # ChainSoTransactionRetriever. \
            # retrieve_transaction(query_output, timestamp)

        if in_txid_set is None and out_txid_set is None:
            return inputs_dict, outputs_dict, connected_dict
        elif in_txid_set is None:
            in_txid_set = set([])
        elif out_txid_set is None:
            out_txid_set = set([])

        txid_set = in_txid_set.union(out_txid_set)
        for txid in txid_set:
            transaction_query = self.CHAIN_SO_TRANSACTION_INFO + str(txid)
            r = safe_requests_get(query=transaction_query, token=None,
                                  timeout=30, jsoncheck=True)
            resp = ChainSoTransactionRetriever. \
                manage_response(transaction_query, r)
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
                for a in in_addr:
                    if a in inputs_dict:
                        inputs_dict[a] += 1
                    else:
                        inputs_dict[a] = 1

            if address in tmp_inputs_list:
                for a in out_addr:
                    if a in outputs_dict:
                        outputs_dict[a] += 1
                    else:
                        outputs_dict[a] = 1

            if address in tmp_inputs_list:
                for a in tmp_inputs_list:
                    if a != address:
                        if a in connected_dict:
                            connected_dict[a] += 1
                        else:
                            connected_dict[a] = 1
            sleep(1)
        return inputs_dict, outputs_dict, connected_dict
