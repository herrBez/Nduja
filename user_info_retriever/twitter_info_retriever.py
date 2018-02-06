import json
from dao.personal_info import PersonalInfo
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from twython import Twython
from twython.exceptions import TwythonRateLimitError
from twython.exceptions import TwythonError
from typing import List


def twitter_safe_show(twython_instance, **params):
    sleep_time = 60
    retry = 0

    while True:
        exception_raised = False

        try:
            result = twython_instance.show(
                **params
            )
        except TwythonRateLimitError:
            logging.info("Wait "
                         + str(sleep_time)
                         + " seconds to avoid being blocked."
                         + " We have already slept "
                         + str(retry)
                         + " minutes")
            retry = retry + 1
            sleep(sleep_time)
            exception_raised = True
        except TwythonError:
            print_json(params)
            sleep(10)
            sys.exit(0)

        if not exception_raised:
            break

    return result



class TwitterInfoRetriever(PersonalInfoRetriever):
    twitter_index = 0
    twitters = [] # type: List[Twython]

    @staticmethod
    def getTwython():
        print(TwitterInfoRetriever.twitter_index)
        print(len(TwitterInfoRetriever.twitters))
        resTwhython = (TwitterInfoRetriever.
                       twitters[TwitterInfoRetriever.twitter_index])
        TwitterInfoRetriever.twitter_index = \
            ((TwitterInfoRetriever.twitter_index + 1) %
             len(TwitterInfoRetriever.twitters))
        return resTwhython

    @staticmethod
    def setToken(tokens):
        print("Set token")
        for i in range(len(tokens["twitter_app_key"])):
            TwitterInfoRetriever.twitters.append(Twython(
                tokens["twitter_app_key"][i],
                tokens["twitter_app_secret"][i],
                tokens["twitter_oauth_token"][i],
                tokens["twitter_oauth_token_secret"][i]))
        print("Token set") 

    def formatURL(self, username):
        if (username is not None):
            twitter_safe_show(TwitterInfoRetriever.getTwython(), screen_name=username)
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
