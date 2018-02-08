import json
import logging
import sys
# from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
# Do not cancel these two imports before twython --> It prevents an infinte
# recursion error due to a bug in grequests (called by twython)

import grequests
import requests

import twython

from address_checkers.eth_address_checker import EthAddressChecker
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from user_info_retriever.info_retriever import InfoRetriever
from wallet_collectors.github_wallet_collector import GithubWalletCollector
from wallet_collectors.searchcode_wallet_collector import \
    SearchcodeWalletCollector
from wallet_collectors.twitter_wallet_collector import TwitterWalletCollector


def search_searchcode(formatfile):
    logging.info("Search Code")
    results = (SearchcodeWalletCollector(formatfile)
               .collect_address())
    Parser().parseString(results)
    return "ok searchcode"


def search_github(formatfile, tokens):
    logging.info("Search Github")
    results = (GithubWalletCollector(formatfile,
                                     tokens
                                     )
               .collect_address())
    logging.info("Finish Search Github")
    Parser().parseString(results)
    return "ok search_github"

def search_twitter(formatfile, tokens):
    results = (TwitterWalletCollector(formatfile,
                                      tokens)
               .collect_address())

    Parser().parseString(results)

    return "ok search_twitter"

if __name__ == "__main__":
    """ This is executed when run from the command line """

    # if len(sys.argv) < 2:
    #     logging.error("python3 %s <search_type>" % sys.argv[0])
    #     sys.exit(0)
    # search_type = sys.argv[1]


    logging.basicConfig(level=logging.INFO)

    config = None
    if (Path('./Nduja/conf.json')).is_file():
        config = json.load(open('./Nduja/conf.json'))
    else:
        logging.error("Config file not found")
        sys.exit(1)

    DbManager.setDBFileName(config["dbname"])
    EthAddressChecker.setToken(config["tokens"]["etherscan"])
    # pool = Pool(processes=3)
    #
    # executor = ThreadPoolExecutor(max_workers=4)
    # f1 = executor.submit(search_github,config["format"],
    #                                    config["tokens"]["github"])
    #
    # f2 = executor.submit(search_twitter, config["format"],
    #                                      config["tokens"])
    # f3 = executor.submit(search_searchcode, config["format"])
    #
    # print("Let's wait")
    #
    # print(f1.result())
    # print(f2.result())
    # print(f3.result())


    # p1 = pool.apply_async(search_github(config["format"],
    #                                     config["tokens"]["github"]), [])
    # p2 = pool.apply_async(search_twitter(config["format"],
    #                                      config["tokens"]), [])
    # p3 = pool.apply_async(search_searchcode(config["format"]), [])
    #
    #
    # pool.join()
    try:
        InfoRetriever.setTokens(config["tokens"])
    except KeyError:
        print()
    # logging.info("Finish to fetch the data. Sleep 15 minutes to let the api ")
    # # sleep(15*62)
    # logging.info("Finish the sleep for the twitter api")
    InfoRetriever().retrieveInfoForAccountSaved()