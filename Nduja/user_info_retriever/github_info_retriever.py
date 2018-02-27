"""Module of class to retrieve info from github accounts"""
from typing import Dict

import requests
from requests import Response

from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from dao.account import Account
from dao.personal_info import PersonalInfo
from utility.print_utility import print_json


class GithubInfoRetriever(PersonalInfoRetriever):
    """Class to retrieve data from bitbucket accounts"""
    URL = "https://api.github.com/users/"
    token = {}  # type: Dict
    current_token = 0

    @staticmethod
    def set_token(token):
        """Set tokens for API requests"""
        GithubInfoRetriever.token = token

    @staticmethod
    def get_token():
        """Get tokenfor API requests"""
        tok = GithubInfoRetriever.token[GithubInfoRetriever.current_token]
        GithubInfoRetriever.current_token = \
            ((GithubInfoRetriever.current_token + 1) %
             len(GithubInfoRetriever.token))
        return tok

    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        res = requests.get(GithubInfoRetriever.format_url(account.username),
                           GithubInfoRetriever.get_token())
        return GithubInfoRetriever.parse_result(res)

    @staticmethod
    def format_url(username: str) -> str:
        """Format URL for the request"""
        if username is None or username.isspace():
            return None
        else:
            to_return = GithubInfoRetriever.URL + username

            if GithubInfoRetriever.token is not None:
                to_return = (to_return + '?access_token=' +
                             (GithubInfoRetriever.
                              token[GithubInfoRetriever.current_token]))
                GithubInfoRetriever.current_token = \
                    (GithubInfoRetriever.current_token + 1) \
                    % len(GithubInfoRetriever.token)
            return to_return

    @staticmethod
    def parse_result(result: Response) -> PersonalInfo:
        """Parse result retrieved"""
        info = None
        if result is not None:
            try:
                info = PersonalInfo(result.json()["name"],
                                    result.json()["blog"],
                                    result.json()["email"],
                                    result.json())
            except KeyError:
                print_json(result.json())
        return info
