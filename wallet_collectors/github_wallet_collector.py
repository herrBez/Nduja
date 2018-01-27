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
        final_result = []
        for f in self.format_object:
            currency_regexp = f["wallet_regexp"]
            currency_name = f["name"]
            currency_symbol = f["symbol"]
            regexp_group = int(f["group"]) # Which group of the regexp should be stored

            raw_result = []
            for page in range(0, 1):
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
                sleep(0.2)

            for item in raw_result:
                try:
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
                        matches_iterator = pattern.finditer(file_content)

                        matches = map(
                            lambda x : x.group(regexp_group),
                            matches_iterator
                        )

                        final_json_element = {
                            "hostname" : "github.com",
                            "username_id" : item["repository"]["owner"]["id"],
                            "username" : item["repository"]["owner"]["login"],
                            "symbol" : currency_symbol,
                            "repo" : item["repository"]["name"],
                            "repo_id" : item["repository"]["id"],
                            "known_raw_url" : download_url,
                            "wallet_list" : list(set(matches))
                        }
                        final_result = final_result + [final_json_element]
                    sleep(0.1)

                except Exception:
                    print("Error on: " + download_url, file=sys.stderr)

        return final_result
pass

# ~ gwc = GithubWalletCollector("../format.json", "../API_KEYS/login.json")
# ~ result=gwc.collect_address()
# ~ print_json(result)
# ~ print(gwc.request_url("http://google.com"))
