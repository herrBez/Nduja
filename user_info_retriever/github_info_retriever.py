from typing import Dict

import grequests
import requests
from requests import Response

from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from dao.account import Account
from dao.personal_info import PersonalInfo
from utility.github_utility import perform_request
from utility.print_utility import print_json

class GithubInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.github.com/users/"
    token = {}  # type: Dict
    current_token = 0

    @staticmethod
    def setToken(token):
        GithubInfoRetriever.token = token

    @staticmethod
    def getToken():
        t = GithubInfoRetriever.token[GithubInfoRetriever.current_token]
        GithubInfoRetriever.current_token = \
            ((GithubInfoRetriever.current_token + 1) %
             len(GithubInfoRetriever.token))
        return t

    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        res = grequests.get(self.formatURL(account.username),
                           headers={
                               "Authorization": "token " +
                                                GithubInfoRetriever.getToken()
                           }
                           )
        # parseResult expects only one Respone. On the contrary
        # perform request expect a List of AsyncRequests and returns a List of
        # Responses
        return self.parseResult(perform_request([res])[0])

    def formatURL(self, username: str) -> str:
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

    def parseResult(self, result: Response) -> PersonalInfo:
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


