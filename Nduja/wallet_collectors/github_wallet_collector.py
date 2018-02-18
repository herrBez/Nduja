import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
import grequests
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep
import pause
import logging
from utility.print_utility import print_json
from utility.github_utility import perform_github_request

from requests import Response
from grequests import AsyncRequest

from typing import List, Iterable, Optional
from typing import Any
from typing import Dict


class GithubWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens) -> None:
        super().__init__(format_file)
        self.format_object = json.load(open(format_file))
        self.max_page = 10
        self.per_page = 100
        self.current_token = 0
        self.tokens = tokens

    def get_next_token(self) -> str:
        token = self.tokens[self.current_token]
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return token

    def collect_raw_result(self, queries: List[str]) -> List[Dict[str, Any]]:
        raw_results_with_url = []  # type: List[Dict[str, Any]]

        # We proceed sequentially to avoid to be blocked for abuses of
        # api.
        for query in queries:
            response = perform_github_request(query, self.get_next_token())

            items = response.json()["items"]

            res_urls = []  # type: List[Response]

            for item in items:
                tmp_res_url = perform_github_request(item["url"],
                                                     self.get_next_token())

                res_urls.append(tmp_res_url)

            for i in range(0, len(res_urls)):
                if res_urls[i] is not None:
                    ru = res_urls[i].json()

                    download_url = ""
                    if "download_url" in ru:
                        download_url = ru["download_url"]

                    tmp = {"known_raw_url": download_url}
                    # print_json(tmp)
                    # ** = all item in a dict
                    raw_results_with_url.append(
                        {
                            **items[i],
                            **tmp
                        }
                    )
                else:
                    logging.warning(str(i) + " res_url is None")

        logging.info("Finish Collection of Raw Results")
        return raw_results_with_url

    def construct_queries(self) -> list:
        word_list = ["donation", "donate", "donating",
                     "contribution", "contribute", "contributing"]
        return [
            "https://api.github.com/search/code?"
            + "q="
            + pattern.symbol
            + "+"
            + word
            + "&page="
            + str(page)
            + "&per_page="
            + str(self.per_page)
            for word in word_list
            for pattern in self.patterns
            for page in range(1, self.max_page+1)
        ]

    def extract_content(self, responses) -> List[str]:
        logging.debug("Entering extract Content")
        contents = []  # type: List[str]

        for response in responses:
            file_content_response = self.request_url(response["known_raw_url"],
                                                     self.get_next_token())

            file_contents = "" if file_content_response is None else \
                            file_content_response.text

            contents.append(file_contents)

        return contents

    def build_answer_json(self, item: Any, content: str,
                          symbol_list: List[str],
                          wallet_list: List[str],
                          emails: Optional[List[str]] =None,
                          websites: Optional[List[str]]=None) \
            -> Dict[str, Any]:

        final_json_element = {
            "hostname": "github.com",
            "text": content,
            "username_id": item["repository"]["owner"]["id"],
            "username": item["repository"]["owner"]["login"],
            # not sure if screen_name = username or not
            # but username is not a field
            "symbol": symbol_list,
            "repo": item["repository"]["name"],
            "repo_id": item["repository"]["id"],
            "known_raw_url": item["known_raw_url"],
            "wallet_list": wallet_list,
            "emails": emails,
            "websites": websites
        }
        return final_json_element


pass

# gwc = GithubWalletCollector("../format.json", "../API_KEYS/login.json")
# result = gwc.collect_address()
# print_json(result)
