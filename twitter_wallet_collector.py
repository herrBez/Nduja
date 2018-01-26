from twython import Twython
import json
import time
from abs_wallet_collector import AbsWalletCollector
import sys
import re
from time import sleep
import traceback


def print_json(s):
        print(json.dumps(s, indent=2))

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
        
    def collect_address(self):
        final_result = []
        for f in self.format_object:
            currency_regexp = f["wallet_regexp"]
            currency_name = f["name"]
            currency_symbol = f["symbol"]
            regexp_group = int(f["group"]) # Which group of the regexp should be stored
            
            result = self.twitter.search(
                q = '%23' + currency_symbol + '%23Donation', # The query: search for hashtags
                count = '30', # Results per page 
                result_type = 'mixed' # search for both popular and not popular content
            )
            
            pattern = re.compile(currency_regexp)
            for r in result["statuses"]:
                content = r["text"]
                try:
                    if pattern.search(content):
                        matches_iterator = pattern.finditer(content)

                        matches = map(
                            lambda x : x.group(regexp_group),
                            matches_iterator
                        )
                        
                        known_raw_url = ''
                        if len(r["entities"]["urls"]) > 0:
                            known_raw_url = r["entities"]["urls"][0]["url"]

                        final_json_element = {
                            "hostname" : "twitter.com",
                            "username_id" : r["user"]["id"],
                            "username" : r["user"]["screen_name"], # not sure if screen_name = username or not, but username is not a field
                            "symbol" : currency_symbol, 
                            "repo" : "",
                            "repo_id" : "",
                            "known_raw_url": known_raw_url,
                            "wallet_list" : list(set(matches))
                        }
                        final_result = final_result + [final_json_element]
                    sleep(0.1)

                except Exception:
                    traceback.print_exc()
                    print("Error on: ", file=sys.stderr)

                
            
            print_json(final_result)
            return final_result

pass

twc = TwitterWalletCollector("format.json", "API_KEYS/twitter.json")
twc.collect_address()
