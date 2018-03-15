"""Module with the class for collecting wallets from searchcode"""
from typing import List, Optional, Iterable, Dict, Any

import logging
from furl import furl
from twython import Twython

from utility.twython_utility import twitter_safe_call
from wallet_collectors.abs_wallet_collector import AbsWalletCollector


class TwitterWalletCollector(AbsWalletCollector):
    """Class for retrieving addresses from Twitter"""
    def __init__(self, format_file: str, tokens_dictionary: Dict) -> None:
        super().__init__(format_file)
        self.twitter_index = 0
        self.api_call_count = []  # type: List[int]
        self.twitters = []  # type: List[Twython]

        for i in range(len(tokens_dictionary["twitter_app_key"])):
            self.twitters.append(Twython(
                tokens_dictionary["twitter_app_key"][i],
                tokens_dictionary["twitter_app_secret"][i],
                tokens_dictionary["twitter_oauth_token"][i],
                tokens_dictionary["twitter_oauth_token_secret"][i]
            ))
            self.api_call_count.append(0)
        self.max_pages = 2
        self.max_count = 100

    def get_twython(self):
        """Return twython object with different API key"""
        self.twitter_index = (self.twitter_index + 1) % len(self.twitters)
        return self.twitter_index

    def inc_api_call_count(self):
        """Increment index of twython used"""
        self.api_call_count[self.twitter_index] += 1

    def twitter_fetch_all_requests(self, query, **kargs):
        """Since the current implementation of cursor contains bug. We should
        iterate over the results manually."""

        my_twitter = self.twitters[self.get_twython()]
        result = twitter_safe_call(my_twitter.search,
                                   q=query,
                                   count=self.max_count,
                                   result_type=kargs["rt"],
                                   tweet_mode="extended")

        logging.info("===")
        if not result:  # The result is empty
            return []

        statuses = result["statuses"]

        logging.info(str(len(result["statuses"])))
        statuses = statuses + result["statuses"]

        # When you no longer receive new results --> stop
        while "next_results" in result["search_metadata"]:
            furl_ = furl(result["search_metadata"]["next_results"])
            my_twitter = self.twitters[self.get_twython()]
            result = twitter_safe_call(my_twitter.search,
                                       q=query,
                                       count=str(self.max_count),
                                       # Results per page
                                       tweet_mode='extended',
                                       result_type=kargs["rt"],
                                       max_id=furl_.args["max_id"])
            if not result:
                break
            logging.info(str(len(result["statuses"])))
            statuses = statuses + result["statuses"]

        logging.info("===")
        return statuses

    def collect_raw_result(self, queries: List[str]) -> List[Any]:
        statuses = []  # type: List[Dict[Any, Any]]
        rt_ = "mixed"
        logging.info("How many queries? %s", str(len(queries)))

        for query in queries:
            statuses = statuses + self.twitter_fetch_all_requests(query,
                                                                  rt=rt_)

        screen_names = list(set([s["user"]["screen_name"] for s in statuses]))

        print("Fetch " + str(len(screen_names)))
        logging.debug("Fetched " + str(len(screen_names))
                      + "screen_names = " + str(screen_names))

        for sn_ in screen_names:
            query = "to:" + sn_

            statuses = statuses + self.twitter_fetch_all_requests(query,
                                                                  rt=rt_)

        return statuses

    def construct_queries(self) -> List[str]:
        queries = []
        for pat in self.patterns:
            for query_filter in ["-filter:retweets AND -filter:replies"]:
                query = ("(" + pat.symbol.lower() + " OR " + pat.name + ")"
                         + " AND (" + "donation OR donate OR donating OR"
                         + " give OR giving OR"
                         + " contribution OR contribute OR contributing "
                         + ") AND " + query_filter)
                queries.append(query)
                query = ("(#" + pat.symbol.lower() + " #GiveAway) OR" + "(#"
                         + pat.symbol.lower() + "GiveAway)" + " AND "
                         + query_filter)
                queries.append(query)
        logging.debug("%s", queries)
        return queries

    @staticmethod
    def extract_content_single(response) -> str:
        """extract a single content"""
        # print(response["full_text"])
        return response["full_text"]

    def extract_content(self, response) -> List[str]:
        return list(map(
            lambda r:
            TwitterWalletCollector.extract_content_single(r),
            response
        ))

    def build_answer_json(self, raw_response: Any, content: str,
                          symbol_list: List[str],
                          wallet_list: List[str],
                          emails: Optional[List[str]] = None,
                          websites: Optional[List[str]] = None) \
            -> Dict[str, Any]:
        known_raw_url = "https://twitter.com/statuses/"\
                        + str(raw_response["id"])

        final_json_element = {
            "hostname": "twitter.com",
            "text": content,
            "username_id": raw_response["user"]["id"],
            "username": raw_response["user"]["screen_name"],
            "symbol": symbol_list,
            "repo": "",
            "repo_id": "",
            "known_raw_url": known_raw_url,
            "wallet_list": wallet_list
        }
        return final_json_element
