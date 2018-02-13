from time import sleep
from typing import List
from typing import Tuple

from dao.wallet import Wallet
from graph.BitcoinTransactionRetriever import BtcTransactionRetriever
from db.db_manager import DbManager
from graph.graph_builder import CurrencyGraph


# Performing a Breadth First Search
def explore(start_addresses: List[Wallet], black_list_address: List[Wallet],
            max_hop: int = 1) -> None:
    btr = BtcTransactionRetriever()

    stack = []  # type: List[Tuple[Wallet, int]]

    g = CurrencyGraph(start_addresses)
    for b in black_list_address:
        g.add_node(b)

    print(start_addresses)

    # avoid duplicates
    addresses = list(set(start_addresses))
    print(addresses)
    for address in addresses:
        stack.append((address, 0))

    already_explored_addresses = set(addresses + black_list_address)
    it = 0

    while len(stack) > 0:
        address, hop = stack.pop(0)
        print(str(len(stack)) + ":" + str(hop))
        print(str(it) + "/" + str(len(start_addresses)))
        it += 1

        # For now exit if hop is 2
        if hop > max_hop:
            break

        already_explored_addresses.add(address)

        in_dict, out_dict, connected_addresses \
            = btr.get_input_output_addresses(address)

        for i in in_dict:
            if i not in already_explored_addresses and i not in stack:
                stack.append((i, hop+1))
                g.add_node(i)
                g.add_str_edge(i, address, weight=in_dict[i])

        for o in out_dict:
            if o not in already_explored_addresses and o not in stack:
                stack.append((o, hop+1))
                g.add_node(o)
                g.add_str_edge(address, o, weight=out_dict[o])

        for o in connected_addresses:
            print(o + " is connected with " + address)

    g.plot(blacklist=black_list_address)


def main() -> None:

    DbManager.setDBFileName("nduja.db")

    db = DbManager.getInstance()

    db.initConnection()

    black_list = db.getAllKnownWallets()

    addresses = [w for w in db.getAllWalletsByCurrency("BTC") if
                 w.address not in black_list]

    db.closeDb()

    if len(addresses) < 1:
        addresses = ["17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j",
                     "1CXEo9yJwU5V3d6FmGyt6ni8KFE26i6t8i"]

    explore(addresses, black_list, max_hop=0)


main()
