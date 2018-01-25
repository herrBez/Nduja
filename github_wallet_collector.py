import json
import requests
from abs_wallet_collector import AbsWalletCollector
import sys
import re
from time import sleep


def print_json(s):
        print(json.dumps(s, indent=2))

class GithubWalletCollector(AbsWalletCollector):    
    base_url="https://api.github.com/search/code?q=$SYMBOL&page=$p&per_page=30"
    
    def __init__(self, format_file, login_file):
        self.format_object = json.loads(open(format_file).read())
        if not (login_file is None):
            self.login_object = json.loads(open(login_file).read())
        
    
    
    def collect_address(self):
        final_json = []
        for f in self.format_object:
            currency_regexp = f["wallet_regexp"]
            currency_name = f["name"]
            currency_symbol = f["symbol"]
            raw_result = []
            for page in range(20,21):
                res = json.loads(
                        self.request_url(
                            "https://api.github.com/search/code?q=" +
                            currency_symbol + 
                            "+Donation"
                            "&page=" + 
                            str(page) +
                            "&per_page=30",
                            self.login_object["token"]
                    )
                )
                raw_result = raw_result + res["items"]
                sleep(0.5)
                
            for item in raw_result:
                res_url = json.loads(
                    self.request_url(
                        item["url"],
                        self.login_object["token"]
                    )
                )
                
                download_url = res_url["download_url"]
                
                file_content = self.request_url(
                        download_url,
                        self.login_object["token"]
                )
                pattern = re.compile(currency_regexp)
                matches = re.findall(pattern, file_content)
                if len(matches) > 0:
                    
                    final_json_element = {
                        "hostname" : "github.com",
                        "username_id" : item["repository"]["owner"]["id"],
                        "username" : item["repository"]["owner"]["login"],
                        "symbol" : currency_symbol,
                        "repo" : item["repository"]["name"],
                        "repo_id" : item["repository"]["id"],
                        "url" : download_url,
                        "wallet_list" : list(set(matches))
                    }
                    final_json = final_json + [final_json_element]
        print_json(final_json)
                    
        return True
pass

gwc = GithubWalletCollector("format.json", "login.json")
gwc.collect_address()

# ~ print(gwc.request_url("http://google.com"))
