import logging
from asyncio import sleep
from typing import Dict, Optional, Set, Any, Tuple
import json
from utility.safe_requests import safe_requests_get
import time


def get_epoch() -> int:
    return int(time.time())


class ChainSoTransactionRetriever:

    CHAIN_SO_INPUT_TRANSACTION = 'https://chain.so/api/v2/get_tx_received/'
    CHAIN_SO_OUTPUT_TRANSACTION = 'https://chain.so/api/v2/get_tx_spent/'
    CHAIN_SO_TRANSACTION_INFO = 'https://chain.so/api/v2/get_tx/'
    timestamp_class = None  # type: Optional[int]

    def __init__(self, currency: str) -> None:
        self.CHAIN_SO_INPUT_TRANSACTION = \
            ChainSoTransactionRetriever.CHAIN_SO_INPUT_TRANSACTION + currency \
            + '/'
        self.CHAIN_SO_OUTPUT_TRANSACTION = \
            ChainSoTransactionRetriever.CHAIN_SO_OUTPUT_TRANSACTION + currency \
            + '/'
        self.CHAIN_SO_TRANSACTION_INFO = \
            ChainSoTransactionRetriever.CHAIN_SO_TRANSACTION_INFO + currency \
            + '/'

    @staticmethod
    def manage_request(query: str, req: Any) -> Optional[Dict[str, Any]]:
        resp = None  # type: Optional[Dict[str, Any]]
        if req is None:
            logging.warning("ChainSoTransactionRetriever " + query
                            + " failed")
        else:
            raw_response = req.text
            try:
                resp = json.loads(raw_response)
            except json.decoder.JSONDecodeError:
                print("Response is not a valid JSON")
                with open('invalid_json.txt', 'a') as the_file:
                    the_file.write(query + "\n")
                print(u' '.join(req.text).encode('utf-8').strip())
                sleep(1)
        return resp

    def get_input_output_addresses(self, address: str,
                                   timestamp: Optional[int] = None) \
            -> Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        timestamp = ChainSoTransactionRetriever.timestamp_class \
            if timestamp is None else timestamp

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        query_input = self.CHAIN_SO_INPUT_TRANSACTION + address
        r = safe_requests_get(query=query_input, token=None, timeout=30,
                              jsoncheck=True)
        resp = ChainSoTransactionRetriever.manage_request(query_input, r)
        if resp is None:
            return inputs_dict, outputs_dict, connected_dict
        txs = resp["data"]["txs"]  # type: Any
        in_txid_set = set([str(t["txid"]) for t in txs if t["time"] < timestamp]) \
        # type: Set[str]

        sleep(1)

        query_output = self.CHAIN_SO_OUTPUT_TRANSACTION + address
        r = safe_requests_get(query=query_output, token=None, timeout=30,
                              jsoncheck=True)
        resp = ChainSoTransactionRetriever.manage_request(query_input, r)
        if resp is None:
            return inputs_dict, outputs_dict, connected_dict
        txs = resp["data"]["txs"]
        out_txid_set = set([str(t["txid"]) for t in txs if t["time"] < timestamp]) \
        # type: Set[str]

        sleep(1)

        txid_set = in_txid_set.union(out_txid_set)
        for txid in txid_set:
            transaction_query = self.CHAIN_SO_TRANSACTION_INFO + str(txid)
            r = safe_requests_get(query=transaction_query, token=None,
                                  timeout=30, jsoncheck=True)
            resp = ChainSoTransactionRetriever.\
                manage_request(transaction_query, r)
            if resp is None:
                return inputs_dict, outputs_dict, connected_dict

            out_addr = {}  # type: Dict[str, int]
            in_addr = {}  # type: Dict[str, int]

            tmp_inputs_list = []
            tmp_outputs_list = []

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
