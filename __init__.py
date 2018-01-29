import configparser
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from pathlib import Path
from wallet_collectors.twitter_wallet_collector import TwitterWalletCollector
import subprocess
import sys
from user_info_retriever.info_retriever import InfoRetriever
from wallet_collectors.github_wallet_collector import GithubWalletCollector
from multiprocessing import Pool
from address_checker.eth_address_checker import EthAddressChecker


def main():
    config = configparser.ConfigParser()
    if (Path('./Nduja/conf.ini')).is_file():
        config.read('./Nduja/conf.ini')
    else:
        config.read('./Nduja/default-conf.ini')
    DbManager.setDBFileName(config.get('file_names', 'dbname'))
    pool = Pool(processes=3)
    p1 = pool.apply_async(searchGithub, [])
    p2 = pool.apply_async(searchTwitter, [])
    # c = pool.apply_async(printNum3, [])
    pool.close()
    pool.join()
    # t1 = \
    #     Thread(target=searchSearchCode(
    #         config.get('file_names', 'result_file')))
    try:
        EthAddressChecker.setToken(config.get('tokens', 'etherscan'))
        tokens = {'github': config.get('tokens', 'github'),
                  'twitter_app_key': config.get('tokens', 'twitter_app_key'),
                  'twitter_app_secret': config.get('tokens',
                                                   'twitter_app_secret'),
                  'twitter_oauth_token': config.get('tokens',
                                                    'twitter_oauth_token'),
                  'twitter_oauth_token_secret': config.get('tokens',
                                                           'twitter_oauth' +
                                                           '_token_secret')}
        InfoRetriever.setTokens(tokens)
    except KeyError:
        print()
    InfoRetriever().retrieveInfoForAccountSaved()


def searchSearchCode(resultPath):
    command = 'cd Nduja && ./address_searcher.sh'
    process = subprocess.Popen(command, shell=True, stdout=sys.stdout)
    process.wait()
    Parser().parseFile(resultPath)


def searchGithub():
    results = (GithubWalletCollector('./Nduja/format.json',
                                     './Nduja/API_KEYS//login.json')
               .collect_address())
    Parser().parseString(results)


def searchTwitter():
    results = (TwitterWalletCollector('./Nduja/format.json',
                                      './Nduja/API_KEYS/twitter.json')
               .collect_address())
    Parser().parseString(results)
