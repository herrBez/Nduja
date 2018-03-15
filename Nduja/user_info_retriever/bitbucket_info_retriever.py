"""Module of class to retrieve info from bitbucket accounts"""
from typing import Optional

import logging
from requests import Response

from utility.safe_requests import safe_requests_get
from dao.account import Account
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever


class BitbucketInfoRetriever(PersonalInfoRetriever):
    """Class to retrieve data from bitbucket accounts"""
    URL = "https://api.bitbucket.org/2.0/users/"

    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        response = safe_requests_get(BitbucketInfoRetriever.
                                     format_url(account.username))
        return BitbucketInfoRetriever.parse_result(response)

    @staticmethod
    def format_url(username: str) -> Optional[str]:
        """Create the url to perform the request"""
        if username is None or username.isspace():
            return None

        return BitbucketInfoRetriever.URL + username

    @staticmethod
    def parse_result(response: Response) -> Optional[PersonalInfo]:
        """Parse the result to find out information"""
        info = None
        if response is not None:
            try:
                info = PersonalInfo(response.json()["display_name"],
                                    response.json()["website"],
                                    None,
                                    response.json())
            except KeyError:
                logging.warning("%s : %s failed the retrieving",
                                str(__file__), str(response.request.url))
        return info

# print(BitbucketInfoRetriever().retrieveInfo('briomkez'))
