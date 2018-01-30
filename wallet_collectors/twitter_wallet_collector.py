import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from furl import furl
from twython import Twython
from wallet_collectors.abs_wallet_collector import flatten

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
        self.max_count = 2

    def collect_raw_result(self, queries):
        statuses = []


        for query in queries:
            for rt in ["mixed", "popular", "recent"]:
                results = self.twitter.cursor(
                    self.twitter.search,
                    q=query,  # The query: search for hashtags
                    count=str(self.max_count),  # Results per page
                    result_type=rt,
                    # search for both popular and not popular content
                    tweet_mode='extended',
                )
                for result in results:
                    statuses = statuses + result["statuses"]

        return flatten(statuses)

    def construct_queries(self) -> list:
        queries = []
        for p in self.patterns:
            for query_filter in ["-filter:retweets AND -filter:replies",
                                 "filter:replies"]:
                query = ("(" + p.symbol.lower() +
                         " OR "
                         + p.name + ")"
                         + "AND ("
                         + "donation OR donate OR donating OR "
                         + "give OR giving"
                         + "contribution OR contribute OR contributing"
                         + "OR providing"
                         + ") AND "
                         + query_filter)
                queries = queries + [query]
        query = ("#" + p.symbol.lower() + "GiveAway" +
                 " AND filter:replies")
        queries = queries + [query]
        return queries

    def extract_content_single(self, response) -> str:
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
