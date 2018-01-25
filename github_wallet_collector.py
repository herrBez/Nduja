import json
import requests
from abs_wallet_collector import AbsWalletCollector
import sys
import re

class GithubWalletCollector(AbsWalletCollector):    
    base_url="https://api.github.com/search/code?q=$SYMBOL&page=$p&per_page=30"
    
    def __init__(self, format_file, login_file):
        self.format_object = json.loads(open(format_file).read())
        if not (login_file is None):
            self.login_object = json.loads(open(login_file).read())
    
    
    def print_json(self, s):
        print(json.dumps(s, indent=2))
    
    
    def collect_address(self):
        for f in self.format_object:
            currency_regexp = f["wallet_regexp"]
            currency_name = f["name"]
            currency_symbol = f["symbol"]
            result = []
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
                result = result + res["items"]
                
            for item in result:
                res_owner = json.loads(
                    self.request_url(
                        item["repository"]["owner"]["url"],
                        self.login_object["token"]
                    )
                )
                
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
                if pattern.search(file_content):
                    print ("Yes")
                    print(item["html_url"])
                    print(item["repository"]["html_url"])
                    print(download_url)
                    
                else:
                    print("No")
                # ~ self.print_json(res_owner)
                # ~ self.print_json(res_url)
                print(file_content)
        
        return True
pass

gwc = GithubWalletCollector("format.json", "login.json")
gwc.collect_address()

# ~ print(gwc.request_url("http://google.com"))
