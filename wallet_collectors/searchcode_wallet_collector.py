import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
import re
from time import sleep

def print_json(s):
    print(json.dumps(s, indent=2))


class SearchcodeWalletCollector(AbsWalletCollector):

    def __init__(self, format_file):
        super().__init__(format_file)
        self.max_page = 10
        self.per_page = 10

    def collect_raw_result(self, query):
        tmp = json.loads(
            self.request_url(
                query
            )
        )
        return tmp["results"]

    def construct_queries(self, pattern) -> list:
        pages = range(0, self.max_page)
        return list(
            map(lambda page:
                "https://searchcode.com/api/codesearch_I/?"
                + "q="
                + pattern.symbol
                + "+Donation"
                + "&p="
                + str(page)
                + "&per_page"
                + str(self.per_page)
                + "&loc=0",
                pages
                )
        )

    def extract_content(self, response) -> str:
        res = ""
        lines = response["lines"]
        for key in lines:
            res += "\n" + lines[key]
        return res

    def build_answer_json(self, item, content, symbol_list, wallet_list):
        repo = item["repo"]
        username_pattern = re.compile("(https?|git)://([^/]*)/([^/]*)/([^/]*)")
        mymatch = username_pattern.search(repo)


        if "bitbucket" in repo:
            hostname = "bitbucket.org"
            username = mymatch.group(4)
        elif "github" in repo:
            hostname = "github.com"
            username = mymatch.group(3)
        elif "google.code" in repo:
            hostname = "google.code.com"
            username = mymatch.group(3)
        elif "gitlab" in repo:
            hostname = "gitlab.com"
            username = mymatch.group(3)
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