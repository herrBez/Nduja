"""Module with the class for collecting wallets from github"""
from typing import List, Iterable, Optional, Any, Dict

import json
import logging

from requests import Response
from tqdm import tqdm

from utility.github_utility import perform_github_request
from wallet_collectors.abs_wallet_collector import AbsWalletCollector


class GithubWalletCollector(AbsWalletCollector):
    """Class for retrieving addresses from Github"""
    def __init__(self, format_file, tokens, progress_bar_postion : int) -> None:
        super().__init__(format_file, progress_bar_postion)
        self.format_object = json.load(open(format_file))
        self.max_page = 1
        self.per_page = 5
        self.current_token = 0
        self.tokens = tokens

    def get_next_token(self) -> str:
        """Get token for API request"""
        token = self.tokens[self.current_token]
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return token

    def collect_raw_result(self, queries: List[str]) -> List[Dict[str, Any]]:
        raw_results_with_url = []  # type: List[Dict[str, Any]]

        # We proceed sequentially to avoid to be blocked for abuses of
        # api.
        for query in tqdm(queries, desc="github" + " "*(15-len("github")),
                          position=self.progress_bar_position,
                          leave=True):
            response = perform_github_request(query, self.get_next_token())
            if response is None:
                with open("none_github_response.txt", "a") as out:
                    out.write(query + "\n")
                continue
            items = response.json()["items"]

            res_urls = []  # type: List[Response]

            for item in items:
                tmp_res_url = perform_github_request(item["url"],
                                                     self.get_next_token())

                res_urls.append(tmp_res_url)

            for i in range(0, len(res_urls)):
                if res_urls[i] is not None:
                    ru_ = res_urls[i].json()

                    download_url = ""
                    if "download_url" in ru_:
                        download_url = ru_["download_url"]

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
                    logging.warning("%s res_url is None", str(i))

        return raw_results_with_url

    def construct_queries(self) -> list:
        word_list = ["donation", "donate", "donating",
                     "contribution", "contribute", "contributing"]
        string_to_search = [p.name for p in self.patterns] + \
                           [p.symbol for p in self.patterns]
        l = [
            "https://api.github.com/search/code?"
            + "q="
            + s
            + "+"
            + word
            + "&page="
            + str(page)
            + "&per_page="
            + str(self.per_page)
            for word in word_list
            for s in string_to_search
            for page in range(1, self.max_page+1)
        ]

        return l

    def extract_content(self, response: List[Any]) -> List[str]:
        logging.debug("Entering extract Content")
        contents = []  # type: List[str]

        for resp in response:
            file_content_response = self.request_url(resp["known_raw_url"],
                                                     self.get_next_token())

            file_contents = "" if file_content_response is None else \
                            file_content_response.text

            contents.append(file_contents)

        return contents

    def build_answer_json(self, raw_response: Any, content: str,
                          symbol_list: List[str],
                          wallet_list: List[str],
                          emails: Optional[List[str]] = None,
                          websites: Optional[List[str]] = None) \
            -> Dict[str, Any]:

        final_json_element = {
            "hostname": "github.com",
            "text": content,
            "username_id": raw_response["repository"]["owner"]["id"],
            "username": raw_response["repository"]["owner"]["login"],
            # not sure if screen_name = username or not
            # but username is not a field
            "symbol": symbol_list,
            "repo": raw_response["repository"]["name"],
            "repo_id": raw_response["repository"]["id"],
            "known_raw_url": raw_response["known_raw_url"],
            "wallet_list": wallet_list,
            "emails": emails,
            "websites": websites
        }
        return final_json_element
