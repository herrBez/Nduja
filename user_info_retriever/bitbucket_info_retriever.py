import requests
import json
from personal_info import PersonalInfo
from abs_personal_info_retriever import PersonalInfoRetriever


class BitbucketInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.bitbucket.org/2.0/users/"

    def retrieveInfo(self, username):
        r = requests.get(BitbucketInfoRetriever.URL + username)
        resp = r.text
        try:
            user = json.loads(resp)
            return PersonalInfo(user["display_name"], user["website"],
                                None, resp)
        except ValueError:
            print()
            return None


# print(BitbucketInfoRetriever().retrieveInfo('briomkez'))
