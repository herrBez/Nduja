import requests
import json
from user_info_retriever.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever


class BitbucketInfoRetriever(PersonalInfoRetriever):
    URL = "https://api.bitbucket.org/2.0/users/"

    def retrieveInfo(self, username):
        if not username.isspace():
            r = requests.get(BitbucketInfoRetriever.URL + username)
            resp = r.text
            try:
                user = json.loads(resp)
                if user["type"] == 'error':
                    return None
                return PersonalInfo(user["display_name"], user["website"],
                                    None, resp)
            except ValueError:
                print()
                return None
        return None


#print(BitbucketInfoRetriever().retrieveInfo('briomkez'))
