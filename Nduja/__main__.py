import json
import logging
import sys
import getopt
from concurrent.futures import ThreadPoolExecutor
# Do not cancel these two imports before twython --> It prevents an infinte
# recursion error due to a bug in grequests (called by twython)
import grequests
import requests
from typing import List

from address_checkers.eth_address_checker import EthAddressChecker
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from wallet_collectors.github_wallet_collector import GithubWalletCollector
from wallet_collectors.searchcode_wallet_collector \
    import SearchcodeWalletCollector
from wallet_collectors.twitter_wallet_collector import TwitterWalletCollector
from user_info_retriever.info_retriever import InfoRetriever


def search_searchcode(formatfile):
    logging.info("Search Code")
    results = (SearchcodeWalletCollector(formatfile)
               .collect_address())
    return results


def search_github(formatfile, tokens):
    logging.info("Search Github")
    results = (GithubWalletCollector(formatfile,
                                     tokens
                                     )
               .collect_address())
    return results


def search_twitter(formatfile, tokens):
    results = (TwitterWalletCollector(formatfile,
                                      tokens)
               .collect_address())


    return results


def print_help():
    print('python3.5 Nduja -t <tasks> -c <conf_file>\n' +
          '<task> could be:\n' +
          '\t* 0 performs all tasks\n' +
          '\t* 1 performs wallet search\n' +
          '\t* 2 performs user info search\n' +
          '\t* 3 performs 1 and 2\n' +
          'default <conf_file> is "./Nduja/conf.json"\n')


def main(argv: List[str]) -> int:
    """ This is executed when run from the command line """
    logging_level = logging.INFO
    tasks = 0
    configfile = 'conf.json'
    if len(argv) > 0:
        try:
            opts, args = getopt.getopt(argv, "ht:c:d",
                                       ["help", "task=", "config=", "debug"])
        except getopt.GetoptError:
            print_help()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print_help()
                sys.exit()
            elif opt in ("-t", "--tasks"):
                tasks = int(arg)
            elif opt in ("-c", "--config"):
                configfile = arg
            elif opt in ("-d", "--debug"):
                logging_level = logging.DEBUG
    print('Tasks is  ', tasks)
    print('Config is ', configfile)
    print('Logging is ', logging_level)
    logging.basicConfig(level=logging_level)
    try:
        config = json.load(open(configfile))
    except FileNotFoundError:
        logging.error("Configuration file not found")
        sys.exit(2)

    DbManager.set_config_file(config["format"])
    DbManager.set_db_file_name(config["dbname"])
    EthAddressChecker.set_token(config["tokens"]["etherscan"])

    if tasks in (0, 1):

        with ThreadPoolExecutor(max_workers=4) as executor:
            f1 = executor.submit(search_github, config["format"],
                                 config["tokens"]["github"])

            f2 = executor.submit(search_searchcode, config["format"])

            f3 = executor.submit(search_twitter, config["format"],
                                 config["tokens"])

        logging.info("Let's wait")


        Parser().parse_string(f1.result())
        Parser().parse_string(f2.result())
        Parser().parse_string(f3.result())



    if tasks in (0, 2):
        try:
            InfoRetriever.set_tokens(config["tokens"])
        except KeyError:
            print()
        InfoRetriever().retrieve_info_for_account_saved()
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
