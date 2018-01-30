import requests
import json
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever


class BitbucketInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.bitbucket.org/2.0/users/"

    def formatURL(self, username):
        if (username is None or username.isspace()):
            return None
        else:
            return (BitbucketInfoRetriever.URL + username)

    def parseResults(self, results):
        infos = []
        for rx in results:
            if rx is not None:
                infos.append(PersonalInfo(rx.json()["display_name"],
                                          rx.json()["website"], "",
                                          rx.json()))
            else:
                infos.append(None)
        return infos

# print(BitbucketInfoRetriever().retrieveInfo('briomkez'))
