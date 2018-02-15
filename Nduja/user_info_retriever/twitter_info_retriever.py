import json
from typing import Dict
from typing import List
from twython import Twython
from dao.personal_info import PersonalInfo
from dao.account import Account
from user_info_retriever.abs_personal_info_retriever \
    import PersonalInfoRetriever
from utility.twython_utility import twitter_safe_call


class TwitterInfoRetriever(PersonalInfoRetriever):
    twitter_index = 0
    twitters = []  # type: List[Twython]

    @staticmethod
    def get_twython() -> Twython:
        res_twhython = (TwitterInfoRetriever.
                        twitters[TwitterInfoRetriever.twitter_index])
        TwitterInfoRetriever.twitter_index = \
            ((TwitterInfoRetriever.twitter_index + 1) %
             len(TwitterInfoRetriever.twitters))
        return res_twhython

    @staticmethod
    def set_token(tokens: Dict) -> None:
        print("Set token")
        for i in range(len(tokens["twitter_app_key"])):
            TwitterInfoRetriever.twitters.append(Twython(
                tokens["twitter_app_key"][i],
                tokens["twitter_app_secret"][i],
                tokens["twitter_oauth_token"][i],
                tokens["twitter_oauth_token_secret"][i]))
        print("Token set")

    def retrieve_info_from_account(self, account: Account) -> PersonalInfo:
        """This method fetches the information for a single Account
        and is specific for each subclass"""
        print("twitter" + account.username)
        result = twitter_safe_call(TwitterInfoRetriever.get_twython().show_user,
                                   screen_name=account.username)
        info = None
        if result is not None:
            info = PersonalInfo(result["name"],
                                result["url"],
                                "",
                                json.dumps(result))

        return info
