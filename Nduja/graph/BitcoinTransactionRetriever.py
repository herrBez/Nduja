
# N.B. In the bitcoin.info there are transactions that contains errors,
# therefore we should treat this kind of errors in the main loop
#
# https://blockchain.info/tx/
# d553e3f89eec8915c294bed72126c7f432811eb821ebee9c4beaae249499058d
import logging
from asyncio import sleep
from typing import Dict, Optional
from typing import List
from typing import Any
from typing import Tuple
import time
import json
import requests
from utility.safe_requests import safe_requests_get


class BtcTransactionRetriever:
    """This class is responsible for collecting the transactions of a given
    address
    """

    BITCOININFO = 'https://blockchain.info/rawaddr/'
    timestamp_class = None  # type: Optional[int]

    # def address_search(self, address: str) -> \
    #         Dict[str, Tuple[List[str], List[str]]]:
    #     """Given an address it returns ALL transactions performed
    #     by the address"""
    #
    #     r = requests.get(BtcTransactionRetriever.BITCOININFO + address)
    #     raw_response = r.text
    #
    #     in_out = {}  # type: Dict[str, Tuple[List[str], List[str]]]
    #
    #     try:
    #         resp = json.loads(raw_response)  # type: Dict[str, Any]
    #
    #         txs = resp["txs"]  # type: Any
    #
    #         for t in txs:
    #             out_addr = {}  # type: Dict[str, int]
    #             in_addr = {}  # type: Dict[str, int]
    #
    #             for o in t["out"]:
    #                 try:
    #                     e = o["addr"]
    #                     if e in out_addr:
    #                         out_addr[e] = out_addr[e] + o["value"]
    #                     else:
    #                         out_addr[e] = o["value"]
    #
    #                 except KeyError:
    #                     logging.error("Corrupted content in bitcoin api:"
    #                                   + "One output address in transaction: "
    #                                   + t["hash"]
    #                                   + " is not valid. Skip this output")
    #
    #             for i in t["inputs"]:
    #                 try:
    #                     e = i["prev_out"]["addr"]
    #                     if e in in_addr:
    #                         in_addr[e] = in_addr[e] + i["prev_out"]["value"]
    #                     else:
    #                         in_addr[e] = i["prev_out"]["value"]
    #                 except KeyError:
    #                     logging.error("Corrupted content in bitcoin api:"
    #                                   + "One input address in transaction: "
    #                                   + t["hash"]
    #                                   + " is not valid. Skip this input")
    #
    #             in_addr_items = in_addr.items()
    #             out_addr_items = out_addr.items()
    #
    #             if address in in_addr_items and address in out_addr_items:
    #
    #                 logging.warning("In btc transaction " + t["hash"] + " " +
    #                                 address + " is in both input and output")
    #
    #             tmp = [(i1[0], i1[1], o1[0], o1[1], t["hash"])
    #                    for i1 in in_addr_items
    #                    for o1 in out_addr_items]
    #
    #             in_out[t["hash"]] = ([i1[0] for i1 in in_addr_items],
    #                                  [o1[0] for o1 in out_addr_items])
    #
    #     except ValueError:
    #         return {}
    #
    #     return in_out

    def get_input_output_addresses(self, address: str,
                                   timestamp: Optional[int] = None) -> \
            Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        timestamp = BtcTransactionRetriever.timestamp_class \
            if timestamp is None else timestamp

        query=BtcTransactionRetriever.BITCOININFO + address
        r = safe_requests_get(query=query,
                              token=None)

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        if r is None:
            logging.warning("BTCTransactionRetriever " + query + " failed")
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

            txs = resp["txs"]  # type: Any

            txs = [t for t in txs if t["time"] < timestamp]

            for t in txs:
                out_addr = {}  # type: Dict[str, int]
                in_addr = {}  # type: Dict[str, int]

                tmp_inputs_list = []
                tmp_outputs_list = []


                for o in t["out"]:
                    try:
                        e = o["addr"]
                        tmp_outputs_list.append(e)
                        out_addr[e] = 1
                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One output address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this output")

                for i in t["inputs"]:
                    try:
                        e = i["prev_out"]["addr"]
                        tmp_inputs_list.append(e)
                        in_addr[e] = 1
                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One input address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this input")

                if set(tmp_outputs_list).intersection(set(tmp_inputs_list)):
                    with open("suspect_transactions.txt", "a") as myfile:
                        myfile.write("===\n")
                        myfile.write(t["hash"] + "\n")
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

        return inputs_dict, outputs_dict, connected_dict
