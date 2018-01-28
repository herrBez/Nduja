import json
from abs_wallet_collector import AbsWalletCollector
from abs_wallet_collector import Pattern
import sys
import re
from time import sleep

def print_json(s):
    print(json.dumps(s, indent=2))


class SearchcodeWalletCollector(AbsWalletCollector):

    def __init__(self, format_file):
        super().__init__(format_file)
        self.max_page = 10
        self.per_page = 1

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
                + "&per_page="
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



        repo_url = item["url"]
        repository = item["name"]
        print("repo " + repository)
        filename = item["filename"]
        print("filename " + filename)
        directory = item["location"]
        print("directory " + directory)

        url = ""

        if directory == "" or directory == "/":
            url = repo_url + "/" + filename
        else:
            url = repo_url + directory + "/" + filename
        print(wallet_list)
        print(url)

        re.compile("(https?|git)://([^/]*)")

        hostname = ""

        if "github.com" in repo_url:
            hostname = "github.com",
            re.compile("")



        final_json_element = {
            "hostname": "github.com",
            "text": content,
            "username_id": "",
            "username": ,
            "symbol": symbol_list,
            "repo": item["repository"]["name"],
            "repo_id": item["repository"]["id"],
            "known_raw_url": "",
            "wallet_list": wallet_list
        }



        return final_json_element



pass

swc = SearchcodeWalletCollector("../format.json")
result = swc.collect_address()
print_json(result)