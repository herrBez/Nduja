import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from furl import furl
from twython import Twython
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep
import logging
import sys


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


    def twitter_fetch_all_requests(self, query, **kargs):

        exception_not_raised = False

        while(True):
            
            try:
                mytwitter = self.twitters[self.getTwython()]
        
                result = mytwitter.search(
                        q=query,  # The query: search for hashtags
                        count=str(self.max_count),  # Results per page
                        result_type=kargs["rt"],
                        # search for both popular and not popular content
                        tweet_mode='extended',
                    )
            except twython.exceptions.TwythonRateLimitError:
                logging.info("Wait 15 minutes to avoid being blocked")
                sleep(15*60 + 2)
                exception_raised = True

            if not exception_raised:
                
            
            
        logging.info("===")
        statuses = result["statuses"]
        
        logging.info(str(len(result["statuses"])))
        statuses = statuses + result["statuses"]

        # When you no longer receive new results --> stop
        while "next_results" in result["search_metadata"]:
            mytwitter = self.twitters[self.getTwython()]
            logging.info("while with query" + query)
            f = furl(result["search_metadata"]["next_results"])
            
            result = mytwitter.search(
                q=query,
                count=str(self.max_count),  # Results per page
                tweet_mode='extended',
                result_type=kargs["rt"],
                max_id=f.args["max_id"]
            )
            logging.info(str(len(result["statuses"])))
            statuses = statuses + result["statuses"]
            
            self.inc_api_call_count()
        logging.info("===")
        return statuses
    

    def collect_raw_result(self, queries):
        statuses = []

        logging.info("How many queries?" + str(len(queries)))


        #~ mytwitter = self.twitters[self.getTwython()]

        #~ logging.info("Search " + queries[2])
        
        #~ result = mytwitter.search(
            #~ q=queries[2],
            #~ count=40,
            #~ result_type="popular",
            #~ # search for both popular and not popular content
            #~ tweet_mode='extended'
        #~ )
        #~ print_json(result)
        #~ sys.exit(1)
            
        

        for query in queries:
            for rt in ["mixed"]: #, "popular", "recent"]:

               statuses = statuses + self.twitter_fetch_all_requests(query,
                                                                    rt=rt
                                                                    )

                
            
        #~ tmp_statuses = list(set(statuses))

        screen_names = list(set([s["user"]["screen_name"] for s in statuses]))

        print("Fetch " + str(len(screen_names)))
        
        for sn in screen_names:
            query = "to:" + sn
            
            statuses = statuses + self.twitter_fetch_all_requests(query,
                                                                  rt=rt
                                                                  )
        
        
        print(screen_names)
             

        return statuses

    def construct_queries(self) -> list:
        queries = []
        for p in self.patterns:
            for query_filter in ["-filter:retweets AND -filter:replies"]:
                
                query = ("(" + p.symbol.lower() +
                         " OR "
                         + p.name + ")"
                         + " AND ("
                         + "donation OR donate OR donating OR"
                         + " give OR giving OR"
                         + " contribution OR contribute OR contributing "
                         + ") AND "
                         + query_filter)
                queries.append(query)
                query = ("(#" + p.symbol.lower() + " #GiveAway) OR"
                         + "(#" + p.symbol.lower() + "GiveAway)"
                         + " AND "
                         + query_filter
                         )
                queries.append(query)
        print(queries)
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
                          wallet_list, emails, websites):
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
