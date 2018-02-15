from time import sleep
from typing import List
from typing import Set
from typing import Tuple
from typing import Dict
from typing import Any

from dao.wallet import Wallet
from graph.BitcoinTransactionRetriever import BtcTransactionRetriever
from db.db_manager import DbManager
# from graph.graph_builder import CurrencyGraph
from graph.cluster import Cluster
from graph.cluster_graph import ClusterGraph



# # Performing a Breadth First Search
# def explore(start_addresses: List[Wallet], black_list_address: List[Wallet],
#             max_hop: int = 1) -> None:
#     btr = BtcTransactionRetriever()
#
#     stack = []  # type: List[Tuple[Wallet, int]]
#
#     g = CurrencyGraph(start_addresses)
#     for b in black_list_address:
#         g.add_node(b)
#
#     print(start_addresses)
#
#     # avoid duplicates
#     addresses = list(set(start_addresses))
#     print(addresses)
#     for address in addresses:
#         stack.append((address, 0))
#
#     already_explored_addresses = set(addresses + black_list_address)
#     it = 0
#
#     while len(stack) > 0:
#         address, hop = stack.pop(0)
#         print(str(len(stack)) + ":" + str(hop))
#         print(str(it) + "/" + str(len(start_addresses)))
#         it += 1
#
#         # For now exit if hop is 2
#         if hop > max_hop:
#             break
#
#         already_explored_addresses.add(address)
#
#         in_dict, out_dict, connected_addresses \
#             = btr.get_input_output_addresses(address)
#
#         for i in in_dict:
#             if i not in already_explored_addresses and i not in stack:
#                 stack.append((i, hop+1))
#                 g.add_node(i)
#                 g.add_str_edge(i, address, weight=in_dict[i])
#
#         for o in out_dict:
#             if o not in already_explored_addresses and o not in stack:
#                 stack.append((o, hop+1))
#                 g.add_node(o)
#                 g.add_str_edge(address, o, weight=out_dict[o])
#
#         for o in connected_addresses:
#             print(o + " is connected with " + address)
#
#     g.plot(blacklist=black_list_address)


def fill_clusters(clusters, black_list=[]):
    btc_transaction_retriever = BtcTransactionRetriever()

    clusters_length = len(clusters)
    processed = 0

    for c in clusters:
        progress = 100*processed/clusters_length

        print("\033[K" + f"processed\t {processed:d} / {clusters_length:d}\t"
              + f"{progress:.2f}%\r", sep=' ', end='', flush=True)
        processed += 1
        stack = set([])
        tmp_black_list = []
        for saddr in c.inferred_addresses:
            stack.add(saddr)

        while len(stack) > 0:
            elem = stack.pop()
            c.add_inferred_address(elem)
            tmp_black_list.append(elem)
            a, b, siblings = btc_transaction_retriever.\
                get_input_output_addresses(elem.address)
            for s in siblings:
                w = Wallet(s, "BTC", "", 1, True)
                if w not in black_list and w not in tmp_black_list:
                    stack.add(w)
    return clusters



def explore_output(clusters: List[Cluster]):
    btc_transaction_retriever = BtcTransactionRetriever()
    for c in clusters:
        output_lists = {} # type: Dict[str, Any]
        output_cluster_list = []
        for w in c.inferred_addresses:
            a, output, siblings = btc_transaction_retriever.get_input_output_addresses(w.address)
            for k in output:  # Take the keys, i.e. the addresses
                output_cluster_list.append(Cluster([Wallet(k, "BTC", "", 1, True)]))
                fill_clusters(Cluster)



def merge_clusters(clusters: List[Cluster]) -> Set[Cluster]:

    clusters_set = set(clusters)

    for c in clusters:
        for d in clusters_set:
            if c == d:
                d.merge_original_list(c)
    return clusters_set



def main() -> None:

    DbManager.set_db_file_name("nduja.db")

    db = DbManager.get_instance()

    db.initConnection()

    black_list = [w for w in db.getAllKnownWallets()]

    clusters = [Cluster([w]) for w in db.getAllWalletsByCurrency("BTC")[3:4] if
                w not in black_list]


    cluster_black_list = [Cluster([w]) for w in black_list]


    print()
    print()
    print()

    db.closeDb()

    fill_clusters(cluster_black_list, black_list=[])

    clusters_set = merge_clusters(clusters)

    print(f"Before {len(clusters):d}: After {len(clusters_set)}")

    # for c in clusters_set:
    #     print("===")
    #     for c1 in c.inferred_addresses:
    #         print(c1)
    #     print("===")

    clusters = list(clusters_set)
    # explore_output(clusters)

    # explore(clusters, black_list=black_list, max_hop=1)

    # explore(addresses, black_list, max_hop=0)

def main2() -> None:
    DbManager.set_db_file_name("nduja.db")

    db = DbManager.get_instance()

    db.init_connection()

    black_list = [w for w in db.get_all_known_wallets()]

    clusters = [Cluster([w]) for w in db.get_all_wallets_by_currency("BTC")[215:216]
                if w not in black_list]

    # cluster_black_list = [Cluster([w]) for w in black_list]

    db.close_db()
    print("qui ci siamo")
    for cluster in clusters:
        cluster.fill_cluster()
        print(len(cluster.inferred_addresses))
    print("Filled")


    clusters_set = set(clusters)

    clusters = list(clusters_set)

    graph = ClusterGraph(clusters_set)

    btc_transaction_retriever = BtcTransactionRetriever()

    print("oki")
    for cluster in clusters:
        for wallet in cluster.inferred_addresses:
            print("Vabbuo")
            input_dict, output_dict, _ = \
                btc_transaction_retriever.\
                get_input_output_addresses(wallet.address)
            print("ok - vabbuo")
            for k in input_dict:
                tmp = Cluster([Wallet(k, "BTC", "", 1, True)])
                graph.add_edge(tmp, cluster)
                #clusters_set.add(tmp)
            for k in output_dict:
                tmp = Cluster([Wallet(k, "BTC", "", 1, True)])
                graph.add_edge(cluster, tmp)
                #clusters_set.add(tmp)
            print("Fatt'")


    print("oki")
    # graph.plot()
    print("Done")

    db.init_connection()

    for c in clusters_set:
        print([str(c1) for c1 in c.inferred_addresses])

    db.insert_clusters(clusters_set)

    db.save_changes()

    db.close_db()


main2()
