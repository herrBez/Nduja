import logging

from db.db_manager import DbManager
from user_info_retriever.bitbucket_info_retriever import BitbucketInfoRetriever
from user_info_retriever.github_info_retriever import GithubInfoRetriever
from user_info_retriever.twitter_info_retriever import TwitterInfoRetriever
from typing import Dict, List
from dao.personal_info import PersonalInfo
import sys
import traceback

class InfoRetriever:
    tokens = None

    @staticmethod
    def set_tokens(tokens: Dict) -> None:
        try:
            GithubInfoRetriever.set_token(tokens['github'])
        except KeyError:
            pass
        try:
            TwitterInfoRetriever.set_token(tokens)
        except KeyError as ke:
            print(ke)
            traceback.print_exc()
            sys.exit(12)

    def retrieve_info_for_account_saved(self) -> None:
        db = DbManager.get_instance()
        db.init_connection()
        accounts = db.get_all_accounts()
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
                    logging.warning(account.host + " not yet supported.")
        info_list = []  # type: List[PersonalInfo]
        if len(githubs) > 0:
            info_list = info_list + GithubInfoRetriever().retrieve_info(githubs)
        if len(bitbuckets) > 0:
            info_list = info_list + \
                        BitbucketInfoRetriever().retrieve_info(bitbuckets)
        if len(twitters) > 0:
            info_list = info_list + \
                        TwitterInfoRetriever().retrieve_info(twitters)
        accounts = []
        accounts = accounts + githubs + bitbuckets + twitters
        acc_info_list = zip(accounts, info_list)
        for (account, info) in acc_info_list:
            if info is not None:
                info_id = (db.insert_information(info.name, info.website,
                                                 info.email, info.json))
                db.add_info_to_account(account.ID, info_id)
        db.save_changes()
