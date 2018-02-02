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
        self.api_call_count = []
        self.twitters = []

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

    def getTwython(self):
        self.twitter_index = (self.twitter_index + 1) % len(self.twitters)
        return self.twitter_index

    def inc_api_call_count(self):
        self.api_call_count[self.twitter_index] += 1


    def collect_raw_result(self, queries):
        statuses = []

        print("How many queries?" + str(len(queries)))

        for query in queries:
            for rt in ["mixed"]: #, "popular", "recent"]:

                mytwitter = self.twitters[self.getTwython()]

                # pages = mytwitter.cursor(
                #     mytwitter.search,
                #     # Search entire pages and not single results
                #     return_pages=True,
                #     q=query,  # The query: search for hashtags
                #     count=str(self.max_count),  # Results per page
                #     result_type=rt,
                #     # search for both popular and not popular content
                #     tweet_mode='extended',
                # )

                result = mytwitter.search(
                    q=query,  # The query: search for hashtags
                    count=str(self.max_count),  # Results per page
                    result_type=rt,
                    # search for both popular and not popular content
                    tweet_mode='extended',
                )
                self.inc_api_call_count()
                print("===")
                print(str(len(result["statuses"])))
                statuses = statuses + result["statuses"]

                # When you no longer receive new results --> stop
                while "next_results" in result["search_metadata"]:
                    print("while with query" + query)
                    f = furl(result["search_metadata"]["next_results"])
                    self.inc_api_call_count()
                    result = mytwitter.search(
                        q=f.args["q"],
                        count=str(self.max_count),  # Results per page
                        # result_type='recent',
                        # search for both popular and not popular content
                        tweet_mode='extended',
                        max_id=f.args["max_id"]
                    )
                    print(str(len(result["statuses"])))
                    statuses = statuses + result["statuses"]
                print("===")
                # page_retrieved = 0
                # for page in pages:
                #     page_retrieved += 1
                #     print("PAGE RETRIEVED" + str(page_retrieved) +
                #           " retrieved " + str(len(page)))
                #     sleep(0.2)
                #     statuses += page
                #     # I get less results than expected
                #     if len(page) < self.max_count - 1:
                #         print("Received less result as maximum. Let's break")
                #         break
                #     else:
                #         print("Din Din Din: " + query)
                #     if page_retrieved > self.max_pages:
                #         break

                #
                # previous_r = ""
                # # Retrieve only self.max_pages pages
                # for i in range(0, self.max_pages):
                #     self.api_call_count[self.twitter_index] += 1
                #     r = next(results)
                #     if r == previous_r:
                #         print("Next and this are equals")
                #
                #
                #     statuses = statuses + r
                #     previous_r = r
                # print(self.api_call_count[self.twitter_index])

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
