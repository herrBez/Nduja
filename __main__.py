#!/usr/bin/env python3
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from pathlib import Path
from wallet_collectors.twitter_wallet_collector import TwitterWalletCollector
from wallet_collectors.searchcode_wallet_collector import SearchcodeWalletCollector
import sys
from user_info_retriever.info_retriever import InfoRetriever
from wallet_collectors.github_wallet_collector import GithubWalletCollector
from multiprocessing import Pool
import json
import twython
from address_checkers.eth_address_checker import EthAddressChecker
from time import sleep
import logging

def search_searchcode(formatfile):
    logging.info("Search Code")
    results = (SearchcodeWalletCollector(formatfile)
               .collect_address())
    Parser().parseString(results)


def search_github(formatfile, tokens):
    logging.info("Search Github")
    results = (GithubWalletCollector(formatfile,
                                     tokens
                                     )
               .collect_address())
    logging.info("Finish Search Github")
    Parser().parseString(results)


def search_twitter(formatfile, tokens):
    try:
        results = (TwitterWalletCollector(formatfile,
                                          tokens)
                   .collect_address())

        Parser().parseString(results)

    except twython.exceptions.TwythonRateLimitError:
        logging.error("Twython rate limit exceed!. Exiting without crash")


if __name__ == "__main__":
    """ This is executed when run from the command line """

    logging.basicConfig(level=logging.DEBUG)

    config = None
    if (Path('./Nduja/conf.json')).is_file():
        config = json.load(open('./Nduja/conf.json'))
    else:
        logging.error("Config file not found")
        sys.exit(1)

    DbManager.setDBFileName(config["dbname"])
    EthAddressChecker.setToken(config["tokens"]["etherscan"])
    pool = Pool(processes=3)

    p1 = pool.apply_async(search_github(config["format"],
                                        config["tokens"]["github"]), [])
    # p2 = pool.apply_async(search_twitter(config["format"],
    #                                      config["tokens"]), [])
    # p3 = pool.apply_async(search_searchcode(config["format"]), [])


    pool.close()
    pool.join()
    try:
        InfoRetriever.setTokens(config)
    except KeyError:
        print()
    logging.info("Finish to fetch the data. Sleep 15 minutes to let the api ")
    # sleep(15*62)
    logging.info("Finish the sleep for the twitter api")
    # InfoRetriever().retrieveInfoForAccountSaved()
