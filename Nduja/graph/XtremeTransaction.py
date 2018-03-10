import http
import socket
import sys
from time import sleep

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from typing import Dict, Optional, Set, List, Any
import json
from decimal import Decimal
import logging

from dao.wallet import Wallet
from db.db_manager import DbManager
from db.db_manager_helper import DbManager2
import psutil

import time
import os
from graph.cluster import Cluster
import subprocess


rpc_port = 2300
rpc_user = "mirko"
rpc_password = "ciaociao"

logging.basicConfig()
myLogger = logging.getLogger(__file__)
myLogger.setLevel(logging.DEBUG)



def get_transaction(rpc_connection, txhash: str) -> Dict:
    return rpc_connection.decoderawtransaction(
        rpc_connection.getrawtransaction(txhash))


def get_block_by_number(rpc_connection, blocknumber: int) -> Dict:
    return rpc_connection.getblock(
        rpc_connection.getblockhash(
            blocknumber
        )
    )


def get_block_by_hash(rpc_connection, blockhash):
    return rpc_connection.getblock(blockhash)


def get_last_block_id(rpc_connection):
    return rpc_connection.getblockcount()


def get_new_rpc_connection():
    return AuthServiceProxy(
        "http://%s:%s@127.0.0.1:%d" % (
            rpc_user,
            rpc_password,
            rpc_port)
    )


def waitUntilReady(rescan: bool = True) -> None:
    sleep_time = 10
    if rescan:
        sleep_time = 60
    while True:
        try:
            get_new_rpc_connection().getinfo()
            break
        except JSONRPCException as e:
            myLogger.debug("waitUntilReady I'm waiting for litecoind")
            sleep(sleep_time)
        except ConnectionError:
            myLogger.debug("waitUntilReady Connection Refused (?)")
            sleep(sleep_time)


def is_running():
    for p in psutil.process_iter():
        if "litecoind" in ' '.join(p.cmdline()):
            return True
    return False


def run(cmd):
    """Tries to start a litecoind instance. Return true if the start
    is successful false otherwise"""
    try:
        myLogger.debug("Run " + str(cmd))
        output = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        myLogger.debug("Ran")
        if "Error" in output.decode():
            return False
        return True
    except subprocess.CalledProcessError:
        return False


def start_server(rescan=True):
    cmdstart = ["litecoind", "-daemon"]

    if is_running():
        stop_server()

    if rescan:
        cmdstart.append("-rescan")
        myLogger.warning("START THE RESCANNING. THIS MAY TAKE A WHILE")
    myLogger.debug("Start Server")

    subprocess.call(cmdstart, stdout=subprocess.PIPE)

    myLogger.debug("Qui")
    sleep(2)
    while True:
        try:
            if not is_running():
                logging.debug("Occhio che non sta girando")
            get_new_rpc_connection().getinfo()
            break
        except JSONRPCException as e:
            # myLogger.debug("JsonRPCException" + str(e.message))
            sleep(2)
        except ConnectionError:
            myLogger.debug("ConnectionError")
            sleep(2)
    #
    # myLogger.debug("After start")
    #
    # tmp = "\"code\":-28"
    # while "\"code\":-28" in str(tmp):
    #     myLogger.debug("In the while")
    #     proc = subprocess.Popen(cmdcheck, stdout=subprocess.PIPE)
    #     sleep(30)
    #     tmp = proc.stdout.read()
    #     myLogger.error("n")
    #
    # sleep(2)
    myLogger.error("y")

    return get_new_rpc_connection()


def stop_server():
    myLogger.debug("Stopping the server")
    while is_running():
        try:
            get_new_rpc_connection().stop()
        except JSONRPCException:
            myLogger.debug("Json RPC. Is the server ready (?)")
            sleep(2)
        except ConnectionError:
            sleep(2)

    myLogger.debug("Server stopped")


# Get the sibling of a single address ^^
def get_sibling(wallet: str,
                all_transactions: List[Any]) -> Set[str]:
    processed_transaction = []
    sibling = set([])

    myLogger.debug("")
    for j in all_transactions:
        potential_sibling = set([])

        if j["txid"] not in processed_transaction:
            processed_transaction.append(j["txid"])
            x = get_transaction(get_new_rpc_connection(), j["txid"])
            wallet_is_input = False
            for t in x["vin"]:
                # It is a coinbase transaction
                if "txid" not in t:
                    myLogger.debug("txid not in t")
                    continue
                t1 = get_transaction(get_new_rpc_connection(), t["txid"])
                addresses = t1["vout"][t["vout"]]["scriptPubKey"]["addresses"]
                potential_sibling = potential_sibling.union(addresses)
                if wallet in addresses:
                    wallet_is_input = True
            if wallet_is_input:
                sibling = sibling.union(potential_sibling)
    if wallet in sibling:
        sibling.remove(wallet)
    return sibling


def get_all_spent_transaction(wallet: str) -> None:
    # Sometimes we have multiple input transaction that have as input our
    # wallet --> we want to avoid to recollect the same trasactions multiple
    # times
    processed_transaction = []

    for j in get_new_rpc_connection().listtransactions("*", 10000, 0, True):
        if j["txid"] not in processed_transaction:
            processed_transaction.append(j["txid"])
            x = get_transaction(get_new_rpc_connection(), j["txid"])
            value_spent = 0
            for t in x["vin"]:
                addresses = []

                # it is a mining reward transaction (== creation of money)
                if "coinbase" in t:
                    myLogger.debug("coinbase not in t:")
                    myLogger.debug(t)
                    myLogger.debug(x["txid"])
                    # t1 = x["vout"][0]["scriptPubKey"]["addresses"]
                    # value = x["vout"]
                # It is a common transaction
                else:
                    t1 = get_transaction(get_new_rpc_connection(), t["txid"])
                    addresses = t1["vout"][t["vout"]]["scriptPubKey"]["addresses"]
                    value = t1["vout"][t["vout"]]["value"]
                if wallet in addresses:
                    # print(addresses)
                    # print(value)
                    # print(x["txid"])
                    # print(t["vout"])
                    # print(value)
                    # print(t1)
                    value_spent += value
            if value_spent > 0:
                print(j["txid"] + " " + str(value_spent))

def main():
    LITECOIN_WALLET_DAT_PATH = "/home/mirko/.litecoin/wallet.dat"
    timestamp = time.time()  # TODO set the right time (1fst march??)
    DbManager.set_db_file_name("./db/nduja_cleaned_wc_no_invalid.db")
    DbManager.set_config_file("../format.json")
    db = DbManager.get_instance()
    db.init_connection()

    currency = "LTC"
    black_list = [w for w in db.get_all_known_wallets_by_currency(currency)]
    black_list_cluster = Cluster(black_list, None, [], [99999])

    wallets = db.get_all_wallets_by_currency(currency)[0:5]

    clusters = []
    wallet2cluster = {}
    for w in wallets:
        if w not in black_list:
            c = Cluster([w], None, [], db.find_accounts_by_wallet(w))
            clusters.append(c)
            wallet2cluster[w] = c

    db_help = DbManager2("prova.sql")
    db_help.init_connection()

    stop_server()
    start_server(rescan=False)

    myLogger.debug("Server started")

    old_sibling = set([])
    new_sibling = set(wallets)
    processed = set([])

    myLogger.debug("Start main loop")

    it = 0
    while len(new_sibling) > 0:

        myLogger.info("Iteration %d. I'll process %d", it, len(new_sibling))

        print("Stopping server")
        stop_server()
        print("Server stopped")

        os.remove(LITECOIN_WALLET_DAT_PATH)
        logging.debug("Removed %s", LITECOIN_WALLET_DAT_PATH)
        start_server(rescan=False)
        processed = processed.union(old_sibling)
        db_help.insert_processed(list(old_sibling))
        db_help.remove_to_process_wallets(list(old_sibling))
        db_help.save_changes()

        for w in new_sibling:
            get_new_rpc_connection().importaddress(w.address, w.address, False)

        myLogger.debug("Loaded all siebling in litecoind")
        stop_server()
        myLogger.debug("Stopped server")
        start_server(rescan=True)
        old_sibling = new_sibling
        new_sibling = set([])

        percentage_step = 1.0/len(old_sibling)
        percentage = 0

        all_transaction = [tx
                           for tx in
                           get_new_rpc_connection().listtransactions("*",
                                                                     1000000,
                                                                     0,
                                                                     True)
                           if tx["time"] < timestamp and
                           "txid" in tx
                           ]

        for w in old_sibling:

            myLogger.debug("%d of total %d", percentage, len(old_sibling))

            percentage += percentage_step

            tmp_new_siebling = set([])
            sibling = [
                Wallet(s, currency, 1, 1) for s in
                get_sibling(w.address, all_transaction).difference([w.address for w in processed])]

            # Add to cluster containing w
            for sw in sibling:
                if sw not in black_list_cluster.inferred_addresses:
                    # we found two clusters that should be merged!
                    if sw in wallet2cluster:
                        # Update the mapping
                        wallet2cluster[sw].merge(wallet2cluster[w])
                        for winf in wallet2cluster[w].inferred_addresses:
                            wallet2cluster[winf] = wallet2cluster[sw]

                    # Simply add the sibling to the cluster
                    else:
                        wallet2cluster[w].add_inferred_address(sw)
                        wallet2cluster[sw] = wallet2cluster[w]
                        myLogger.debug("Add " + sw.address + " to cluster of "
                                       + w.address)

                    tmp_new_siebling.add(sw)

                # It is in the black list ->  executed at most once in a loop
                else:
                    for sw1 in sibling:
                        wallet2cluster[w].add_inferred_address(sw1)
                        wallet2cluster[sw1] = wallet2cluster[w]

                    # Cancel from mapping the black list one
                    for winf in wallet2cluster[w].inferred_addresses:
                        wallet2cluster.pop(winf, None)
                    wallet2cluster.pop(w, None)

                    black_list_cluster.merge(wallet2cluster[w])
                    myLogger.debug("Merge cluster of " + w + " in black_list")
                    # Clear the tmp_new_siebling. We won't explore black list
                    # wallets
                    tmp_new_siebling = set([])
                    break
            print(len(tmp_new_siebling))
            new_sibling = new_sibling.union(tmp_new_siebling)
        it += 1
        new_sibling.difference(old_sibling)

    myLogger.info("Exiting normally...")


if __name__ == "__main__":
    main()
