import json
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from twython import Twython


class TwitterInfoRetriever(PersonalInfoRetriever):
    twitter_index = 0
    twitters = []

    def getTwython():
        resTwhython = (TwitterInfoRetriever.
                       twitters[TwitterInfoRetriever.twitter_index])
        TwitterInfoRetriever.twitter_index = \
            ((TwitterInfoRetriever.twitter_index + 1) %
             len(TwitterInfoRetriever.twitters))
        return resTwhython

    def setToken(tokens):
        for i in range(len(tokens["twitter_app_key"])):
            TwitterInfoRetriever.twitters.append(Twython(
                tokens["twitter_app_key"][i],
                tokens["twitter_app_secret"][i],
                tokens["twitter_oauth_token"][i],
                tokens["twitter_oauth_token_secret"][i]))

    def formatURL(self, username):
        if (username is not None):
            TwitterInfoRetriever.getTwython().show_user(screen_name=username)
        else:
            return None

    def retrieveInfo(self, usernames):
        results = []
        [results.append(self.formatURL(username)) for username in usernames]
        return None

    def parseResults(self, results):
        infos = []
        for rx in results:
            if rx is not None:
                infos.append(PersonalInfo(rx["name"], rx["url"], "",
                                          json.dumps(rx)))
            else:
                infos.append(None)
        return infos

# TwitterInfoRetriever.setToken(
#     app_key="",
#     app_secret="",
#     oauth_token="",
#     oauth_token_secret="")
# print(TwitterInfoRetriever().retrieveInfo('asgadhghdfha'))
