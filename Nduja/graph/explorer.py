from time import sleep
from typing import List
from typing import Tuple

from graph.BitcoinTransactionRetriever import BtcTransactionRetriever
from db.db_manager import DbManager
from graph.graph_builder import CurrencyGraph


# Performing a Breadth First Search
def explore(start_addresses: List[str], black_list_address: List[str]) -> None:
    btr = BtcTransactionRetriever()

    stack = []  # type: List[Tuple[str, int]]

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
        if hop > 0:
            break

        already_explored_addresses.add(address)

        in_dict, out_dict = btr.get_input_output_addresses(address)

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

    g.plot(blacklist=black_list_address)


def main() -> None:

    DbManager.setDBFileName("nduja.db")

    db = DbManager.getInstance()

    db.initConnection()

    black_list = [w.address for w in db.getAllKnownWallets()]

    db.closeDb()

    db.initConnection()

    print(len(db.getAllWalletsByCurrency("BTC")))

    db.closeDb()

    db.initConnection()

    addresses = [w.address for w in db.getAllWalletsByCurrency("BTC") if
                 w.address not in black_list]

    db.closeDb()

    print(len(black_list))

    print(len(addresses))

    if len(addresses) < 1:
        addresses = ["17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j", "1CXEo9yJwU5V3d6FmGyt6ni8KFE26i6t8i"]

    explore(addresses, black_list)


main()
