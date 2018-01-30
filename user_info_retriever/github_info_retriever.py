from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
import grequests
import requests


class GithubInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.github.com/users/"
    token = None
    current_token = 0

    def setToken(token):
        GithubInfoRetriever.token = token

    def getToken():
        t = GithubInfoRetriever.token[GithubInfoRetriever.current_token]
        GithubInfoRetriever.current_token = \
            ((GithubInfoRetriever.current_token + 1) %
             len(GithubInfoRetriever.token))
        return t

    def formatURL(self, username):
        if (username is None or username.isspace()):
            return None
        else:
            toReturn = GithubInfoRetriever.URL + username

            if GithubInfoRetriever.token is not None:
                toReturn = (toReturn + '?access_token=' +
                            (GithubInfoRetriever.
                                token[GithubInfoRetriever.current_token]))
                GithubInfoRetriever.current_token = \
                    (GithubInfoRetriever.current_token + 1) \
                    % len(GithubInfoRetriever.token)
            return toReturn

    def parseResults(self, results):
        infos = []
        for rx in results:
            if rx is not None:
                infos.append(PersonalInfo(rx.json()["name"], rx.json()["blog"],
                                          rx.json()["email"], rx.json()))
            else:
                infos.append(None)
        return infos

    def retrieveInfo(self, accounts):
        reqs = []
        [reqs.append(self.formatURL(account.username))
         for account in accounts]
        rs = (grequests.get(q,
                            headers={
                                'Authorization': 'token ' +
                                GithubInfoRetriever.getToken()}) for q in reqs)
        return self.parseResults(grequests.map(rs))

# print(GithubInfoRetriever().retrieveInfo('mzanella'))
