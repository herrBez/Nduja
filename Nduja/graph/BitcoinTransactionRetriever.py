import json
import requests
import logging

from graph.graph_builder import CurrencyGraph

def print_json(s):
    """pretty print a json string"""
    print(json.dumps(s, indent=2))


class BtcTransactionRetriever:

    BITCOININFO = 'https://blockchain.info/rawaddr/'

    @staticmethod
    def address_search(addr):
        '''Checks if the bitcoin address exists'''
        r = requests.get(BtcTransactionRetriever.BITCOININFO + addr)
        resp = r.text

        in_out = []


        try:
            resp = json.loads(resp)



            txs = resp["txs"]

            for t in txs:
                # On bitcoin.info there are transactions that contains errors:
                # https://blockchain.info/tx/d553e3f89eec8915c294bed72126c7f432811eb821ebee9c4beaae249499058d
                out_addr = {}
                in_addr = {}

                for o in t["out"]:
                    try:
                        e = o["addr"]
                        if e in out_addr:
                            out_addr[e] = out_addr[e] + o["value"]
                        else:
                            out_addr[e] = o["value"]

                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One output address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this output")

                for i in t["inputs"]:
                    try:
                        e = i["prev_out"]["addr"]
                        if e in out_addr:
                            in_addr[e] = in_addr[e] + i["prev_out"]["value"]
                        else:
                            in_addr[e] = i["prev_out"]["value"]
                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One input address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this input")

                in_addr = in_addr.items()
                out_addr = out_addr.items()



                if addr in in_addr and addr in out_addr:
                    logging.warning("In btc transaction " + t["hash"] + " " +
                                    addr + " is in both input and output")

                tmp = [(i1, o1, t["hash"]) for i1 in in_addr for o1 in out_addr]
                in_out += list(set(tmp))


        except ValueError:
            return (0,0,0)

        return (addr, in_out)


# Usage example
c = BtcTransactionRetriever()
addr = '1NBakuExebh2M9atfS3QuSmRPPtYU398VN'

addr, tr = BtcTransactionRetriever.address_search(addr)

print(tr)

g = CurrencyGraph([addr])

for (i, o, h) in tr:
    g.add_edge(i[0], o[0], trx=h, ivalue=i[1], ovalue=o[1])

for (i, o, h) in tr:
    g.add_edge(i[0], o[0], trx=h, ivalue=i[1], ovalue=o[1])

print("Loaded. Now Print")

g.plot_multigraph()


# print(c.address_search('1EQ1aVN4Au7adKTT6JXtSpnz75HVVNkMmp'))
# print(c.address_check("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))
# print(c.address_check('16hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
# print(c.address_check('6hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
