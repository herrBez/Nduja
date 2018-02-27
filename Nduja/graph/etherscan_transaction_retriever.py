
# N.B. In the bitcoin.info there are transactions that contains errors,
# therefore we should treat this kind of errors in the main loop
#
# https://blockchain.info/tx/
# d553e3f89eec8915c294bed72126c7f432811eb821ebee9c4beaae249499058d
import logging
from time import sleep
from typing import Dict
from typing import List
from typing import Any
from typing import Tuple

import json
import requests
from utility.safe_requests import safe_requests_get


class EtherscanTransactionRetriever:
    """This class is responsible for collecting the transactions of a given
    address
    """
    ETHERSCAN_INFO = 'http://api.etherscan.io/api?' \
                     'module=account&action=txlist&address='
    ETHERSCAN_TOKEN_API = 'apikey='

    def __init__(self, tokens: List[str] = None) -> None:
        self.tokens = tokens
        self.token_index = 0

    def build_query(self, address: str):
        query = EtherscanTransactionRetriever.ETHERSCAN_INFO + address
        if self.tokens is not None and len(self.tokens) > 0:
            query += (EtherscanTransactionRetriever.ETHERSCAN_INFO +
                      self.tokens[self.token_index])
            self.token_index = ((self.token_index + 1) %
                                len(self.tokens))
        return query

    def get_input_output_addresses(self, address: str) -> \
            Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""
        query = self.build_query(address)
        r = safe_requests_get(query=query,
                              token=None)

        sleep(0.15)

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        if r is None:
            logging.warning("EtherscanTransactionRetriever " + query
                            + " failed")
        else:

            raw_response = r.text

            try:
                resp = json.loads(raw_response)  # type: Dict[str, Any]
            except json.decoder.JSONDecodeError:
                print("Response is not a valid JSON")
                with open('invalid_json.txt', 'a') as the_file:
                    the_file.write(query + "\n")
                print(u' '.join(r.text).encode('utf-8').strip())
                sleep(1)
                return inputs_dict, outputs_dict, connected_dict

            txs = resp["result"]  # type: Any

            for t in txs:
                from_address = t["from"].strip()
                to_address = t["to"].strip()

                if from_address != 'GENESIS' and to_address != 'GENESIS' \
                        and len(from_address) > 0 and len(to_address) > 0:
                    if from_address == address:
                        if to_address in outputs_dict:
                            outputs_dict[to_address] += 1
                        else:
                            outputs_dict[to_address] = 1
                    elif to_address == address:
                        if from_address in inputs_dict:
                            inputs_dict[from_address] += 1
                        else:
                            inputs_dict[from_address] = 1

                    if from_address == to_address:
                        with open("eth_suspect_transactions.txt", "a") as myfile:
                            myfile.write("===\n")
                            myfile.write(t["hash"] + "\n")
                            myfile.write("===\n")

        return inputs_dict, outputs_dict, {}
