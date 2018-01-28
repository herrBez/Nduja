import json
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from twython import Twython


class TwitterInfoRetriever(PersonalInfoRetriever):
    twitter = None

    def setToken(app_key, app_secret, oauth_token, oauth_token_secret):
        if TwitterInfoRetriever.twitter is None:
            TwitterInfoRetriever.twitter = Twython(app_key, app_secret,
                                                   oauth_token,
                                                   oauth_token_secret)

    def retrieveInfo(self, username):
        if not username.isspace():
            user = TwitterInfoRetriever.twitter.show_user(screen_name=username)
            try:
                return PersonalInfo(user["name"], user["url"],
                                    None, json.dumps(user))
            except ValueError:
                print()
                return None
        return None


# TwitterInfoRetriever.setToken(
#     app_key="",
#     app_secret="",
#     oauth_token="",
#     oauth_token_secret="")
# print(TwitterInfoRetriever().retrieveInfo('asgadhghdfha'))
