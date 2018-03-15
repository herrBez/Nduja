"""Module for the class that retrieve information for different accounts"""
from typing import Dict, List

import sys
import logging
import traceback

from db.db_manager import DbManager
from user_info_retriever.github_info_retriever import GithubInfoRetriever
from user_info_retriever.twitter_info_retriever import TwitterInfoRetriever
from user_info_retriever.bitbucket_info_retriever import BitbucketInfoRetriever
from dao.personal_info import PersonalInfo


class InfoRetriever:
    """Class for retrieve information from accounts"""
    tokens = None

    @staticmethod
    def set_tokens(tokens: Dict) -> None:
        """Set tokens for different API requests"""
        try:
            GithubInfoRetriever.set_token(tokens['github'])
        except KeyError:
            pass
        try:
            TwitterInfoRetriever.set_token(tokens)
        except KeyError as key_err:
            print(key_err)
            traceback.print_exc()
            sys.exit(12)

    def retrieve_info_for_account_saved(self) -> None:
        """Retrieve information from account saved into the database"""
        database = DbManager.get_instance()
        database.init_connection()
        accounts = database.get_all_accounts()
        githubs = []
        bitbuckets = []
        twitters = []
        for account in accounts:
            if account.info is None:
                if "github" in account.host:
                    githubs.append(account)
                elif "bitbucket" in account.host:
                    bitbuckets.append(account)
                elif "twitter" in account.host:
                    twitters.append(account)
                else:
                    logging.warning("%s not yet supported.", account.host)
        info_list = []  # type: List[PersonalInfo]
        if githubs:
            info_list = info_list + GithubInfoRetriever().retrieve_info(githubs)
        if bitbuckets:
            info_list = info_list + \
                        BitbucketInfoRetriever().retrieve_info(bitbuckets)
        if twitters:
            info_list = info_list + \
                        TwitterInfoRetriever().retrieve_info(twitters)
        accounts = []
        accounts = accounts + githubs + bitbuckets + twitters
        acc_info_list = zip(accounts, info_list)
        for (account, info) in acc_info_list:
            if info is not None:
                info_id = (database.insert_information(info.name, info.website,
                                                       info.email, info.json))
                database.add_info_to_account(account.ID, info_id)
        database.save_changes()
