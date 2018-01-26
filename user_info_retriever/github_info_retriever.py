import requests
import json
from user_info_retriever.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever


class GithubInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.github.com/users/"
    token = None

    def setToken(token):
        GithubInfoRetriever.token = token

    def formatURL(username):
        toReturn = GithubInfoRetriever.URL + username
        if GithubInfoRetriever.token is not None:
            toReturn = toReturn + '?access_token=' + GithubInfoRetriever.token
        return toReturn

    def retrieveInfo(self, username):
        if not username.isspace():
            r = requests.get(GithubInfoRetriever.formatURL(username))
            resp = r.text
            try:
                print("username: " + username)
                user = json.loads(resp)
                print(user)
                return PersonalInfo(user["name"], user["blog"],
                                    user["email"], resp)
            except ValueError:
                print()
                return None
        return None


# print(GithubInfoRetriever().retrieveInfo('mzanella'))
