import configparser
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from pathlib import Path
from wallet_collectors.twitter_wallet_collector import TwitterWalletCollector
import subprocess
import sys
from user_info_retriever.info_retriever import InfoRetriever
from threading import Thread


def main():
    config = configparser.ConfigParser()
    if (Path('./Nduja/conf.ini')).is_file():
        config.read('./Nduja/conf.ini')
    else:
        config.read('./Nduja/default-conf.ini')
    DbManager.setDBFileName(config.get('file_names', 'dbname'))
    # t1 = \
    #     Thread(target=searchSearchCode(
    #         config.get('file_names', 'result_file')))
    t2 = Thread(target=searchTwitter)
    # t1.start()
    t2.start()
    # t1.join()
    t2.join()
    try:
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


def searchTwitter():
    results = str(TwitterWalletCollector('./Nduja/format.json',
                                         './Nduja/API_KEYS/twitter.json')
                  .collect_address())
    Parser().parseString(results)
