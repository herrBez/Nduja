import configparser
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from pathlib import Path
import subprocess
import sys
from user_info_retriever.info_retriever import InfoRetriever


def main():
    config = configparser.ConfigParser()
    if (Path('./Nduja/conf.ini')).is_file():
        config.read('./Nduja/conf.ini')
    else:
        config.read('./Nduja/default-conf.ini')
    DbManager.setDBFileName(config.get('file_names', 'dbname'))
    command = 'cd Nduja && ./address_searcher.sh'
    process = subprocess.Popen(command, shell=True, stdout=sys.stdout)
    process.wait()
    Parser().parse(config.get('file_names', 'result_file'))
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
