import configparser
from db.db_manager import DbManager
from result_parser.parsing_results import Parser
from pathlib import Path
import subprocess
import sys
from user_info_retriever.info_retriever import InfoRetriever
from github_wallet_collector import GithubWalletCollector
from threading import Thread


def main():
    config = configparser.ConfigParser()
    if (Path('./Nduja/conf.ini')).is_file():
        config.read('./Nduja/conf.ini')
    else:
        config.read('./Nduja/default-conf.ini')
    DbManager.setDBFileName(config.get('file_names', 'dbname'))
    t1 = \
        Thread(target=searchSearchCode(
            config.get('file_names', 'result_file')))
    t2 = Thread(target=searchGithub)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    try:
        tokens = {'github': config.get('tokens', 'github')}
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
    results = str(GithubWalletCollector(("/mnt/3C013B4060E799D6/Desktop/cns/Nduja/format.json"),
                                        ("/mnt/3C013B4060E799D6/Desktop/cns/Nduja/API_KEYS/login.json"))
                  .collect_address())
    results = results.replace("'", '"').replace(
        "wallet_list", "wallet").replace("hostname", "host")
    results = '{"results" : ' + results + '}'
    Parser().parseString(results)
