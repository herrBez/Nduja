import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
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
        self.max_count = 100

    def collect_raw_result(self, query):
        statuses = []
        count_pages = 0

        for rt in ["mixed", "popular", "recent"]:
            result = self.twitter.search(
                q=query,  # The query: search for hashtags
                count=str(self.max_count),  # Results per page
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
                    count=str(self.max_count),  # Results per page
                    # result_type='recent',
                    # search for both popular and not popular content
                    tweet_mode='extended',
                    max_id=f.args["max_id"]
                )
                statuses = statuses + result["statuses"]
                count_pages = count_pages + 1

        return statuses

    def construct_queries(self, p) -> list:
        queries = []
        for query_filter in ["-filter:retweets AND -filter:replies",
                             "filter:replies"]:
            query = (p.symbol.lower() +
                     " AND donation AND " +
                     query_filter)
            queries = queries + [query]
        return queries

    def extract_content(self, response) -> str:
        return response["full_text"]

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
