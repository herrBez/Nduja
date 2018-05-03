from typing import List
from typing import Set
from typing import Dict
from typing import Any
import time

import logging
import sys
from dao.wallet import Wallet
from graph.abs_transaction_retriever import AbsTransactionRetriever
from graph.bitcoin_transaction_retriever import BtcTransactionRetriever
from db.db_manager import DbManager
from graph.cluster import Cluster
from graph.doge_transaction_retriever import DogeTransactionRetriever
from graph.etherscan_transaction_retriever import EtherscanTransactionRetriever
from graph.ltc_transaction_retriever import LtcTransactionRetriever
from tqdm import tqdm


def fill_clusters(clusters, black_list=[]):
    btc_transaction_retriever = BtcTransactionRetriever()

    for c in tqdm(clusters):
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


def explore_output(clusters: List[Cluster],
                   transaction_retriever: AbsTransactionRetriever):
    for c in clusters:
        output_lists = {}  # type: Dict[str, Any]
        output_cluster_list = []
        for w in c.inferred_addresses:
            a, output, siblings = transaction_retriever.\
                get_input_output_addresses(w.address)
            for k in output:  # Take the keys, i.e. the addresses
                output_cluster_list.append(Cluster(
                    [Wallet(k, "BTC", "", 1, True)], transaction_retriever))
                fill_clusters(Cluster)


def merge_clusters(clusters: List[Cluster]) -> Set[Cluster]:

    clusters_set = set(clusters)

    for c in clusters:
        for d in clusters_set:
            if c == d:
                d.merge_original_list(c)
    return clusters_set


def get_epoch() -> int:
    return int(time.time())


def get_retriever_by_currency(currency: str) -> AbsTransactionRetriever:
    return {
        "BTC":  BtcTransactionRetriever(),
        "LTC":  LtcTransactionRetriever(),
        "DOGE": DogeTransactionRetriever(),
        "ETH":  EtherscanTransactionRetriever()
    }[currency]


def main2(argv: List[str]) -> None:
    """
        Requires 2 arguments:
         - first -> db name
         - second -> currency (BTC, ETH, LTC, DOGE)
    """
    DbManager.set_db_file_name(argv[1])
    db = DbManager.get_instance()
    db.init_connection()

    currency = argv[2] if argv[2] in ["BTC", "ETH", "LTC", "DOGE"] \
        else "LTC"

    epoch = get_epoch()
    AbsTransactionRetriever.timestamp_class = epoch
    transaction_retriever = get_retriever_by_currency(currency)

    black_list = [w for w in db.get_all_known_wallets_by_currency(currency)]

    clusters = [Cluster([w], transaction_retriever, [],
                        db.find_accounts_by_wallet(w))
                for w in db.get_all_wallets_by_currency(currency)
                if w not in black_list]

    black_list_cluster = Cluster(black_list, transaction_retriever, [], [99999])

    db.close_db()

    logging.info("Starting the fill cluster function")
    length = len(clusters)

    times = 0
    for cluster in tqdm(clusters):
        cluster.fill_cluster(black_list_cluster)


    clusters = [cluster for cluster in clusters
                if not cluster.belongs_to_black_list]
    clusters_set = set(clusters)
    clusters = list(clusters_set)

    db.init_connection()
    db.insert_clusters(clusters)
    db.save_changes()
    db.close_db()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main2(sys.argv)
