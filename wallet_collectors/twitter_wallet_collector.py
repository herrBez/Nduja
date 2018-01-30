import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from furl import furl
from twython import Twython
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep


def print_json(s):
    print(json.dumps(s, indent=2))


class TwitterWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens_dictionary):
        super().__init__(format_file)

        print_json(tokens_dictionary)

        self.twitter_index = 0
        self.twitters = []

        for i in range(len(tokens_dictionary["twitter_app_key"])):
            self.twitters.append(Twython(
                tokens_dictionary["twitter_app_key"][i],
                tokens_dictionary["twitter_app_secret"][i],
                tokens_dictionary["twitter_oauth_token"][i],
                tokens_dictionary["twitter_oauth_token_secret"][i]
            ))
        self.max_pages = 3
        self.max_count = 100

    def getTwython(self):
        resTwhython = self.twitters[self.twitter_index]
        self.twitter_index = (self.twitter_index + 1) % len(self.twitters)
        return resTwhython

    def collect_raw_result(self, queries):
        statuses = []

        print("How many queries?" + str(len(queries)))

        for query in queries:
            for rt in ["mixed", "popular", "recent"]:
                mytwitter = self.getTwython()

                results = mytwitter.cursor(
                    mytwitter.search,
                    return_pages=True,
                    q=query,  # The query: search for hashtags
                    count=str(self.max_count),  # Results per page
                    result_type=rt,
                    # search for both popular and not popular content
                    tweet_mode='extended',
                )
                # Retrieve only self.max_pages pages
                for i in range(0, self.max_pages):
                    r = next(results)
                    statuses = statuses + r

        return statuses

    def construct_queries(self) -> list:
        queries = []
        for p in self.patterns:
            for query_filter in ["-filter:retweets AND -filter:replies",
                                 "filter:replies"]:
                query = ("(" + p.symbol.lower() +
                         " OR "
                         + p.name + ")"
                         + " AND ("
                         + "donation OR donate OR donating OR "
                         + "give OR giving OR"
                         + " contribution OR contribute OR contributing "
                         + ") AND "
                         + query_filter)
                queries = queries + [query]
        query = ("#" + p.symbol.lower() + "GiveAway" +
                 " AND filter:replies")
        queries = queries + [query]
        return queries

    def extract_content_single(self, response) -> str:
        # print(response["full_text"])
        return response["full_text"]

    def extract_content(self, responses):
        return list(map(
            lambda r:
            self.extract_content_single(r),
            responses
        ))

    def build_answer_json(self, raw_response, content, symbol_list,
                          wallet_list):
        known_raw_url = ''
        if len(raw_response["entities"]["urls"]) > 0:
            known_raw_url = raw_response["entities"]["urls"][0]["url"]

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


pass

# twc = TwitterWalletCollector("../format.json", "../API_KEYS/twitter.json")
# result1 = json.dumps(twc.collect_address())
# results = '{"results" : ' + result1 + '}'
# with open("scr.txt", mode='a') as file:
#     file.write(results)
