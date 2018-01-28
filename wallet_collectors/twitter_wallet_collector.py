import json
import re
import sys
import traceback
from functools import reduce
from time import sleep
from abs_wallet_collector import AbsWalletCollector
from abs_wallet_collector import Pattern
from furl import furl
from twython import Twython


def print_json(s):
    print(json.dumps(s, indent=2))


class TwitterWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, login_file):
        super().__init__(format_file)
        login_object = json.loads(open(login_file).read())
        self.twitter = Twython(
            login_object["APP_KEY"],
            login_object["APP_SECRET"],
            login_object["OAUTH_TOKEN"],
            login_object["OAUTH_TOKEN_SECRET"]
        )

    def collect_raw_result(self, query):
        statuses = []
        count_pages = 0

        for rt in ["mixed", "popular", "recent"]:
            result = self.twitter.search(
                q=query,  # The query: search for hashtags
                count='100',  # Results per page
                result_type=rt,
                # search for both popular and not popular content
                tweet_mode='extended',
            )
            statuses = statuses + result["statuses"]

            # When you no longer receive new results --> stop
            while "next_results" in result["search_metadata"]:
                f = furl(result["search_metadata"]["next_results"])

                result = self.twitter.search(
                    q=f.args["q"],
                    count='100',  # Results per page
                    # result_type='recent',
                    # search for both popular and not popular content
                    tweet_mode='extended',
                    max_id=f.args["max_id"]
                )
                statuses = statuses + result["statuses"]
                count_pages = count_pages + 1

        return statuses

    def collect_address(self):
        final_result = []

        for f in self.format_object:

            currency_symbol = f["symbol"]
            statuses = []

            for query_filter in ["-filter:retweets AND -filter:replies",
                                 "filter:replies"]:
                query = (currency_symbol.lower()
                         + " AND donation AND "
                         + query_filter)
                statuses = statuses + self.collect_raw_result(query)

            for r in statuses:
                content = r["full_text"]
                try:
                    # Retrieve the list of matches
                    match_list = list(
                        map(lambda x: x.match(content), self.patterns)
                    )
                    # Reduce the list of lists to a single list
                    match_list = reduce(
                        lambda x, y: x + y,
                        match_list,
                        []
                    )

                    if len(match_list) > 0:

                        symbol_list, wallet_list = map(list, zip(*match_list))

                        known_raw_url = ''
                        if len(r["entities"]["urls"]) > 0:
                            known_raw_url = r["entities"]["urls"][0]["url"]

                        final_json_element = {
                            "hostname": "twitter.com",
                            "text": r["full_text"],
                            "username_id": r["user"]["id"],
                            "username": r["user"]["screen_name"],
                            # not sure if screen_name = username or not, but username is not a field
                            "symbol": symbol_list,
                            "repo": "",
                            "repo_id": "",
                            "known_raw_url": known_raw_url,
                            "wallet_list": wallet_list
                        }
                        final_result = final_result + [final_json_element]

                    sleep(0.1)

                except Exception:
                    traceback.print_exc()
                    print("Error on: ", file=sys.stderr)

        return final_result


pass

twc = TwitterWalletCollector("../format.json", "../API_KEYS/twitter.json")
result1 = twc.collect_address()
print_json(result1)