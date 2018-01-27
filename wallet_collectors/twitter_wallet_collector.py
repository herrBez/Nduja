from twython import Twython
import json
import time
from abs_wallet_collector import AbsWalletCollector
import sys
import re
from time import sleep
import traceback
from furl import furl


def print_json(s):
    print(json.dumps(s, indent=2))


class Pattern:
    def __init__(self, format_object):
        self.pattern = re.compile(format_object["wallet_regexp"])
        self.name = format_object["name"]
        self.group = format_object["group"]
        self.symbol = format_object["symbol"]

    def match(self, content):
        matches = []
        if self.pattern.search(content):
            matches_iterator = self.pattern.finditer(content)

            matches = list(
                map(
                    lambda x:
                        (self.symbol, x.group()),
                    matches_iterator
                )
            )
        return matches


class TwitterWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, login_file):
        self.format_object = json.loads(open(format_file).read())
        login_object = json.loads(open(login_file).read())
        self.twitter = Twython(
            login_object["APP_KEY"],
            login_object["APP_SECRET"],
            login_object["OAUTH_TOKEN"],
            login_object["OAUTH_TOKEN_SECRET"]
        )
        self.patterns = []
        for f in self.format_object:
            print_json(f)
            self.patterns.append(Pattern(f))

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
            currency_regexp = f["wallet_regexp"]
            # currency_name = f["name"]
            currency_symbol = f["symbol"]
            # Which group of the regexp should be stored
            regexp_group = int(f["group"])
            pattern = re.compile(currency_regexp)

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
                    if pattern.search(content):
                        print("===\n")
                        for p in self.patterns:
                            print(p.match(content))

                        match_list = list(
                            map(lambda x: x.match(content), self.patterns))
                        for ml in match_list:
                            print(ml)


                    # match_list = list(map(lambda x: x.match(content), self.patterns))
                    # print(match_list)
                    # print("===\n")

                        matches_iterator = pattern.finditer(content)

                        matches = map(
                            lambda x: x.group(regexp_group),
                            matches_iterator
                        )

                        known_raw_url = ''
                        if len(r["entities"]["urls"]) > 0:
                            known_raw_url = r["entities"]["urls"][0]["url"]
                        # ~ else:
                        # ~ print_json(r)
                        # ~ sleep(2)
                        final_json_element = {
                            "hostname": "twitter.com",
                            "text": r["full_text"],
                            "username_id": r["user"]["id"],
                            "username": r["user"]["screen_name"],
                            # not sure if screen_name = username or not, but username is not a field
                            "symbol": currency_symbol,
                            "repo": "",
                            "repo_id": "",
                            "known_raw_url": known_raw_url,
                            "wallet_list": tuple(list(set(matches)))
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
print_json([dict(t) for t in set([tuple(d.items()) for d in result1])])
