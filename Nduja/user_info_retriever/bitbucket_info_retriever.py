import grequests
import requests
from requests import Response
from dao.account import Account
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever


class BitbucketInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.bitbucket.org/2.0/users/"

    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        response = requests.get(self.format_url(account.username))
        return self.parse_result(response)

    def format_url(self, username: str) -> str:
        if username is None or username.isspace():
            return None

        return BitbucketInfoRetriever.URL + username

    def parse_result(self, response: Response) -> PersonalInfo:
        info = None
        if response is not None:
            info = PersonalInfo(response.json()["display_name"],
                                response.json()["website"],
                                None,
                                response.json())
        return info

# print(BitbucketInfoRetriever().retrieveInfo('briomkez'))
