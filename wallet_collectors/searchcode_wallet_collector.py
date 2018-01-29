import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
import re
from time import sleep
import grequests
import requests

def print_json(s):
    print(json.dumps(s, indent=2))

def exception_handler(request, exception):
        print(exception)

class SearchcodeWalletCollector(AbsWalletCollector):

    def __init__(self, format_file):
        super().__init__(format_file)
        self.max_page = 10
        self.per_page = 10

    def collect_raw_result(self, queries):
        rs = (grequests.get(q) for q in queries)
        raw_results = grequests.imap(rs, exception_handler=exception_handler)
        raw_results = list(
            map(lambda r:
                r.json()["results"],
                raw_results
                )
        )

        return raw_results

    def construct_queries(self) -> list:
        return [
            "https://searchcode.com/api/codesearch_I/?"
            + "q="
            + pattern.symbol
            + "+Donation"
            + "&p="
            + str(page)
            + "&per_page"
            + str(self.per_page)
            + "&loc=0"
            for pattern in self.patterns
            for page in range(0, self.max_page)
        ]

    def extract_content(self, response) -> str:
        res = ""
        lines = response["lines"]
        for key in lines:
            res += "\n" + lines[key]
        return res

    def build_answer_json(self, item, content, symbol_list, wallet_list):
        repo = item["repo"]
        username_pattern = re.compile("(https?|git)://([^/]*)/([^/]*)/([^/]*)")
        my_match = username_pattern.search(repo)


        if "bitbucket" in repo:
            hostname = "bitbucket.org"
            username = my_match.group(4)
        elif "github" in repo:
            hostname = "github.com"
            username = my_match.group(3)
        elif "google.code" in repo:
            hostname = "google.code.com"
            username = my_match.group(3)
        elif "gitlab" in repo:
            hostname = "gitlab.com"
            username = my_match.group(3)
        else:
            # Not known source
            hostname = ""
            username = ""

        final_json_element = {
            "hostname": hostname,
            "text": content,
            "username_id": "",
            "username": username,
            "symbol": symbol_list,
            "repo": repo,
            "repo_id": "",
            "known_raw_url": item["url"],
            "wallet_list": wallet_list
        }

        return final_json_element

pass

# swc = SearchcodeWalletCollector("../format.json")
# result = swc.collect_address()
# print(result)