import configparser
from db_manager import DbManager
from parsing_results import Parser
from pathlib import Path


def main():
    config = configparser.ConfigParser()
    if (Path('./Nduja/conf.ini')).is_file():
        config.read('./Nduja/conf.ini')
    else:
        config.read('./Nduja/default-conf.ini')
    DbManager.setDBFileName(config['file_names']['db'])
    Parser().parse(config['file_names']['result_file'])
