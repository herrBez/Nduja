"""Module for retrieving addresses input of the same transaction locally"""
from typing import Dict, Optional, Set, List, Any

import http
import socket
import sys
import math
import os
import subprocess
import time
from time import sleep
import json
from decimal import Decimal
import logging

import psutil
from tqdm import tqdm
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from dao.wallet import Wallet
from db.db_manager import DbManager
from db.db_manager_helper import DbManager2
from graph.cluster import Cluster
import subprocess

from tqdm import tqdm
from pathlib import Path


RPC_PORT = 2300
RPC_USER = ""
RPC_PASSWORD = ""
COMMAND = ""

logging.basicConfig()
MY_LOGGER = logging.getLogger(__file__)
MY_LOGGER.setLevel(logging.DEBUG)

ERROR_FILE_PATH = "transaction_wo_adresses.json"

def safe_rpc_call(func):
    while True:
        try:
            ret = func()
            break
        except Exception:
            sleep(0.1)
    return ret


def get_transaction(rpc_connection, txhash: str) -> Dict:
    return safe_rpc_call(lambda: get_new_rpc_connection().decoderawtransaction(
        rpc_connection.getrawtransaction(txhash)))


def get_block_by_number(rpc_connection, blocknumber: int) -> Dict:
    return safe_rpc_call(lambda:
                         rpc_connection.getblock(
                             rpc_connection.getblockhash(
                                 blocknumber
                             )
                         )
    )


def get_block_by_hash(rpc_connection, blockhash):
    return safe_rpc_call(lambda: rpc_connection.getblock(blockhash))


def get_last_block_id(rpc_connection):
    return safe_rpc_call(lambda: rpc_connection.getblockcount())


def get_new_rpc_connection(timeout: int = 40):
    return AuthServiceProxy(
        "http://%s:%s@127.0.0.1:%d" % (
            RPC_USER,
            RPC_PASSWORD,
            RPC_PORT),
        timeout=timeout
    )


def wait_until_ready(rescan: bool = True) -> None:
    sleep_time = 10
    timeout = 40
    if rescan:
        sleep_time = 60
    while True:
        try:
            get_new_rpc_connection(timeout=timeout).getinfo()
            break
        except JSONRPCException:
            MY_LOGGER.debug("waitUntilReady I'm waiting for litecoind")
            sleep(sleep_time)
        except socket.timeout:
            timeout += 20
        except ConnectionError:
            MY_LOGGER.debug("waitUntilReady Connection Refused (?)")
            sleep(sleep_time)


def is_running():
    for p in psutil.process_iter():
        if COMMAND in p.name():
            return True
    return False


def run(cmd):
    """Tries to start a litecoind instance. Return true if the start
    is successful false otherwise"""
    try:
        MY_LOGGER.debug("Run " + str(cmd))
        output = subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        MY_LOGGER.debug("Ran")
        # pylint: disable=no-member
        if "Error" in output.decode():
            # pylint: enable=no-member
            return False
        return True
    except subprocess.CalledProcessError:
        return False


def start_server(rescan=True):
    cmdstart = [COMMAND]

    if is_running():
        stop_server()

    if rescan:
        cmdstart.append("-rescan")
        MY_LOGGER.warning("START THE RESCANNING. THIS MAY TAKE A WHILE")
    MY_LOGGER.debug("Start Server")

    subprocess.call(cmdstart, stdout=subprocess.PIPE)

    MY_LOGGER.debug("Start server process started in background")
    sleep(2)
    while True:
        try:
            if not is_running():
                logging.debug("Occhio che non sta girando")
            get_new_rpc_connection().getinfo()
            break
        except JSONRPCException:
            # myLogger.debug("JsonRPCException" + str(e.message))
            sleep(2)
        except ConnectionError:
            MY_LOGGER.debug("ConnectionError")
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
    MY_LOGGER.error("y")

    return get_new_rpc_connection()


def stop_server():
    MY_LOGGER.debug("Stopping the server")
    MY_LOGGER.debug(is_running())
    while is_running():
        try:
            get_new_rpc_connection().stop()
        except JSONRPCException:
            MY_LOGGER.debug("Json RPC. Is the server ready (?)")
            sleep(2)
        except ConnectionError:
            sleep(2)

    MY_LOGGER.debug("Server stopped")


def pre_elaborate(all_transaction):
    # Mapping transaction("txid") -> [Input Addresses]
    transactions = {}

    for j in tqdm(all_transaction):
        x = get_transaction(get_new_rpc_connection(), j["txid"])
        transactions[j["txid"]] = set([])
        for t in x["vin"]:
            # It is a coinbase transaction
            if "txid" not in t:
                MY_LOGGER.debug("txid not in t")
                continue
            t1 = get_transaction(get_new_rpc_connection(), t["txid"])
            try:
                transactions[j["txid"]] = \
                    transactions[j["txid"]].union(
                        set(t1["vout"][t["vout"]]["scriptPubKey"]["addresses"])
                    )
            except KeyError:
                with open(ERROR_FILE_PATH, "a") as f:
                    f.write(t1["txid"])
                    f.write("\n")

    return transactions

# Get the sibling of a single address ^^
# to achieve better performances -->
# all_transactions SHOULD NOT CONTAIN DUPLICATES
def get_sibling(wallet: str,
                transactions: dict) -> Set[str]:
    sibling = set([])  # type: Set[str]

    for k in tqdm(transactions):
        if wallet in transactions[k]:
            sibling = sibling.union(transactions[k])
    if wallet in sibling:
        sibling.remove(wallet)
    return sibling


def get_all_spent_transaction(wallet: str) -> None:
    # Sometimes we have multiple input transaction that have as input our
    # wallet --> we want to avoid to recollect the same trasactions multiple
    # times
    processed_transaction = []  # type: List[Any]

    for j in get_new_rpc_connection().listtransactions("*", 10000, 0, True):
        if j["txid"] not in processed_transaction:
            processed_transaction.append(j["txid"])
            x = get_transaction(get_new_rpc_connection(), j["txid"])
            value_spent = 0
            for t in x["vin"]:
                addresses = []  # type: List[Any]

                # it is a mining reward transaction (== creation of money)
                if "coinbase" in t:
                    MY_LOGGER.debug("coinbase not in t:")
                    MY_LOGGER.debug(t)
                    MY_LOGGER.debug(x["txid"])
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


def retrieve_all_raw_transactions_alt(timestamp):
    txs_processed = 0
    all_transaction = []
    fixed_step = 1000000
    new_transactions = [0]
    while len(new_transactions) > 0:
        timeout = 60
        while True:
            try:
                new_transactions = (get_new_rpc_connection(timeout=timeout).
                                    listtransactions("*",
                                                     txs_processed
                                                     + fixed_step,
                                                     txs_processed + 1,
                                                     True))

                all_transaction += [tx
                                    for tx in
                                    new_transactions
                                    if tx["time"] < timestamp and
                                    "txid" in tx]
                break
            except socket.timeout:
                sleep(2)  # Sleep and retry
                logging.warning("All Transaction failed for timeout!: "
                                + "Let's retry")
                timeout *= 2
                if not is_running():
                    start_server(rescan=False)
            except Exception as e:
                MY_LOGGER.debug(type(e))
                sleep(1)
        txs_processed += fixed_step
    return all_transaction


def retrieve_all_raw_transactions(timestamp):
    timeout = 60
    while True:
        try:
            all_transaction = [tx
                               for tx in
                               (get_new_rpc_connection(timeout=timeout).
                                listtransactions("*",
                                                 100000000,
                                                 0,
                                                 True))
                               if tx["time"] < timestamp and "txid" in tx]
            break
        except socket.timeout:
            sleep(2)  # Sleep and retry
            logging.warning("All Transaction failed for timeout!: "
                            + "Let's retry")
            timeout *= 2
            if not is_running():
                start_server(rescan=False)
    return all_transaction


def main(currency):
    with open(ERROR_FILE_PATH, "a") as f:
        f.write("Run of " + str(time.time()) + "\n")
    timestamp = time.time()  # TODO set the right time (1fst march??)
    DbManager.set_db_file_name("./db/nduja_cleaned_wc_no_invalid.db")
    DbManager.set_config_file("../format.json")
    db = DbManager.get_instance()
    db.init_connection()

    db_help = DbManager2("prova.db")
    db_help.init_connection()

    processed_wallets = set([w.address for w in db_help.wallets_processed()])
    wallets = set(db.get_all_wallets_by_currency(currency))
    clusters = db.retrieve_clusters_by_currency(currency)

    wallet2cluster = {}

    MY_LOGGER.debug("Building the wallet2cluster mapping ... ")
    for c in tqdm(clusters):
        for w in c.inferred_addresses:
            wallet2cluster[w] = c
    MY_LOGGER.debug("Built ... ")


    # find the black list cluster and remove it
    for c in clusters:
        if 99999 in c.ids:
            black_list_cluster = c
            break
    clusters.remove(c)
    MY_LOGGER.debug("Find the black list cluster")

    wallets_wo_processed = wallets.difference(processed_wallets)

    total_to_process = len(wallets_wo_processed)

    to_process = wallets_wo_processed[0:min(total_to_process, 100)]

    MY_LOGGER.debug("We should process %d wallets. Let's go with the first %d",
                    total_to_process,
                    len(to_process))

    old_sibling = set([])
    new_sibling = set(to_process)
    processed = set([])

    MY_LOGGER.debug("Start main loop")

    it = 0


    while new_sibling:

        MY_LOGGER.info("Iteration %d. I'll process %d", it, len(new_sibling))

        print("Stopping server")
        print(is_running())
        stop_server()
        print("Server stopped")

        # Altough the process is stopped, it is a good idea to wait some time,
        # because otherwise we could have race conditions (or at least, it is
        # my experience)

        sleep(0.5)
        os.remove(WALLET_DAT_PATH)
        logging.debug("Removed %s", WALLET_DAT_PATH)
        start_server(rescan=False)
        processed = processed.union(old_sibling)
        db_help.insert_processed(list(old_sibling))
        db_help.save_changes()

        for w in tqdm(new_sibling):
            get_new_rpc_connection().importaddress(w.address, w.address, False)

        MY_LOGGER.debug("Loaded all siebling in litecoind")
        stop_server()
        MY_LOGGER.debug("Stopped server")
        start_server(rescan=True)
        old_sibling = new_sibling
        new_sibling = set([])

        percentage_step = 100.0/len(old_sibling)
        percentage = 0

        all_transaction = retrieve_all_raw_transactions_alt(timestamp)

        logging.debug("all_transaction length Before "
                      + str(len(all_transaction)))

        all_transaction = list({tx["txid"]: tx
                                for tx in all_transaction}.values())

        logging.debug("all_transaction length After "
                      + str(len(all_transaction)))

        all_transaction = pre_elaborate(all_transaction)
        # print(all_transaction)

        for w in old_sibling:
            assert w in wallet2cluster

        for w in old_sibling:

            MY_LOGGER.debug("%0.3f %c of total %d", percentage, '%', len(old_sibling))

            percentage += percentage_step

            tmp_new_siebling = set([])
            sibling = [
                Wallet(s, currency, "", 1, 1) for s in
                get_sibling(w.address, all_transaction).difference([w.address for w in processed])]

            # Add to cluster containing w
            for sw in sibling:
                if sw not in black_list_cluster.inferred_addresses:
                    # we found two clusters that should be merged!
                    if sw in wallet2cluster:
                        # Update the mapping
                        wallet2cluster[w].merge(wallet2cluster[sw])
                        for winf in wallet2cluster[sw].inferred_addresses:
                            wallet2cluster[winf] = wallet2cluster[w]

                    # Simply add the sibling to the cluster
                    else:
                        wallet2cluster[w].add_inferred_address(sw)
                        wallet2cluster[sw] = wallet2cluster[w]
                        MY_LOGGER.debug("Add " + sw.address + " to cluster of "
                                        + w.address)

                    tmp_new_siebling.add(sw)

                # It is in the black list ->  executed at most once in a loop
                else:

                    for sw1 in sibling:
                        if sw1 in wallet2cluster:
                            wallet2cluster[w].merge(wallet2cluster[sw1])
                        else:
                            wallet2cluster[w].add_inferred_address(sw1)
                        wallet2cluster[sw1] = wallet2cluster[w]

                    add_wallets = wallet2cluster[w].inferred_addresses

                    black_list_cluster.merge(wallet2cluster[w])

                    for sw1 in add_wallets:
                        wallet2cluster[sw1] = black_list_cluster

                    # Clear the tmp_new_sibling. We won't explore black list
                    # wallets
                    tmp_new_siebling = set([])
                    break
            print(len(tmp_new_siebling))
            new_sibling = new_sibling.union(tmp_new_siebling)
        it += 1
        new_sibling = new_sibling.difference(old_sibling)
        MY_LOGGER.debug("New Sibling Length = %d", len(new_sibling))

    MY_LOGGER.info("Exiting normally...")

    for i in range(black_list_cluster.inferred_addresses):
        black_list_cluster.inferred_addresses[i].status = -1

    clusters = list(set([wallet2cluster[w] for w in wallet2cluster]))
    db.insert_clusters(clusters)
    db.save_changes()
    db.init_connection()


if __name__ == "__main__":
    if len(sys.argv) < 6:
        logging.error("Usage python3 %s "
                      + "<currency>"
                      + "<rpc_user> "
                      + "<rpc_password>"
                      + "<servercmd>"
                      + "<data-dir>"
                      , sys.argv[0])
        sys.exit(1)

    currency = sys.argv[1]
    RPC_USER = sys.argv[2]
    RPC_PASSWORD = sys.argv[3]
    COMMAND = sys.argv[4]
    WALLET_DAT_PATH = sys.argv[5] + "/wallet.dat"

    main(currency)