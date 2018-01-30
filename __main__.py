#!/usr/bin/env python3
import configparser
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

def search_searchcode():
    print("Search Code")
    results = (SearchcodeWalletCollector('./Nduja/format.json')
               .collect_address())
    Parser().parseString(results)


def search_github(tokens):
    print("Search Github")
    results = (GithubWalletCollector('./Nduja/format.json',
                                     tokens
                                     )
               .collect_address())
    Parser().parseString(results)


def search_twitter(tokens):
    try:
        results = (TwitterWalletCollector('./Nduja/format.json',
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
        # config.read('./Nduja/default-conf.ini')

    # tokens = {'github': config["tokens"]["github"],
    #           'twitter_app_key': config["tokens"]["twitter_app_key"],
    #           'twitter_app_secret': config["tokens"]["twitter_app_secret"],
    #           'twitter_oauth_token': config["tokens"][
    #               "twitter_oauth_token"],
    #           'twitter_oauth_token_secret': config["tokens"][
    #               'twitter_oauth_token_secret']
    #           }

    DbManager.setDBFileName(config["dbname"])
    pool = Pool(processes=3)
    p1 = pool.apply_async(search_github(config["github"]), [])
    p2 = pool.apply_async(search_twitter(config["tokens"]), [])
    p3 = pool.apply_async(search_searchcode(), [])

    print("ciao")
    pool.close()
    pool.join()

    # t1 = \
    #     Thread(target=searchSearchCode(
    #         config.get('file_names', 'result_file')))
    # try:
    #     # tokens = {'github': config["tokens"]["github"],
    #     #           'twitter_app_key': config["tokens"]["twitter_app_key"],
    #     #           'twitter_app_secret': config["tokens"][
    #     #               "twitter_app_secret"],
    #     #           'twitter_oauth_token': config["tokens"][
    #     #               "twitter_oauth_token"],
    #     #           'twitter_oauth_token_secret': config["tokens"][
    #     #               'twitter_oauth' +
    #     #               '_token_secret']
    #     #           }
    #     # InfoRetriever.setTokens(tokens)
    # except KeyError:
    #     print()
    # InfoRetriever().retrieveInfoForAccountSaved()


