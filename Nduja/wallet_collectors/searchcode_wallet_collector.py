import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
import re
from time import sleep
import grequests
import requests
from wallet_collectors.abs_wallet_collector import flatten
from utility.print_utility import print_json
import logging

from typing import Dict, Optional
from typing import Any
from typing import List


def exception_handler(request, exception):
        print(exception)


class SearchcodeWalletCollector(AbsWalletCollector):

    def __init__(self, format_file):
        super().__init__(format_file)
        self.max_page = 10
        self.per_page = 20

    def collect_raw_result(self, queries: List[str]) -> List[Any]:
        rs = (grequests.get(q) for q in queries)
        raw_responses = grequests.imap(rs, exception_handler=exception_handler)
        raw_results = list(
            map(lambda r:
                r.json()["results"],
                raw_responses
                )
        )

        return flatten(raw_results)

    def construct_queries(self) -> List[str]:
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

    def extract_content_single(self, response) -> str:
        res = ""
        lines = response["lines"]
        for key in lines:
            res += "\n" + lines[key]
        return res

    def extract_content(self, responses: List[Any]) -> List[str]:
        return list(map(
            lambda r:
            self.extract_content_single(r),
            responses
        ))

    def build_answer_json(self, item: Any, content: str,
                          symbol_list: List[str],
                          wallet_list: List[str],
                          emails: Optional[List[str]]=None,
                          websites: Optional[List[str]]=None)\
            -> Dict[str, Any]:
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
            logging.warning("Repo of type " + repo + " not yet supported")
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