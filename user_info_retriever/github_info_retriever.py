import requests
import json
from personal_info import PersonalInfo
from abs_personal_info_retriever import PersonalInfoRetriever


class GithubInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.github.com/users/"

    def retrieveInfo(self, username):
        r = requests.get(GithubInfoRetriever.URL + username)
        resp = r.text
        try:
            user = json.loads(resp)
            return PersonalInfo(user["name"], user["blog"],
                                user["email"], resp)
        except ValueError:
            print()
            return None


# print(GithubInfoRetriever().retrieveInfo('mzanella'))
