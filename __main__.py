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


def search_searchcode(formatfile):
    print("Search Code")
    results = (SearchcodeWalletCollector(formatfile)
               .collect_address())
    Parser().parseString(results)


def search_github(formatfile, tokens):
    print("Search Github")
    results = (GithubWalletCollector(formatfile,
                                     tokens
                                     )
               .collect_address())
    Parser().parseString(results)


def search_twitter(formatfile, tokens):
    try:
        results = (TwitterWalletCollector(formatfile,
                                          tokens)
                   .collect_address())
        print("Twitter gave " + len(results) + " results")
        Parser().parseString(results)

    except twython.exceptions.TwythonRateLimitError:
        print("Twython rate limit exceed!. Exiting without crash")


if __name__ == "__main__":
    """ This is executed when run from the command line """
    config = None
    if (Path('./Nduja/conf.json')).is_file():
        config = json.load(open('./Nduja/conf.json'))
    else:
        print("Error config file not found")
        sys.exit(1)

    DbManager.setDBFileName(config["dbname"])
    EthAddressChecker.setToken(config["tokens"]["etherscan"])
    pool = Pool(processes=3)
    p1 = pool.apply_async(search_github(config["format"],
                                        config["tokens"]["github"]), [])
    p2 = pool.apply_async(search_twitter(config["format"],
                                         config["tokens"]), [])
    p3 = pool.apply_async(search_searchcode(config["format"]), [])
    pool.close()
    pool.join()
    # try:
    #     # InfoRetriever.setTokens(config)
    # except KeyError:
    #     print()
    # InfoRetriever().retrieveInfoForAccountSaved()
