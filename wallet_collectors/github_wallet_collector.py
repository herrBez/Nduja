import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from wallet_collectors.abs_wallet_collector import Pattern
import sys
import grequests
import requests
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep

def print_json(s):
    print(json.dumps(s, indent=2))

def exception_handler(request, exception):
    print("error with request")


class GithubWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens):
        super().__init__(format_file)
        self.format_object = json.load(open(format_file))
        self.max_page = 2
        self.per_page = 30
        self.current_token = 0
        self.tokens = tokens

    def request_url(self, url, token=None):
        r = super().request_url(url, self.tokens[self.current_token])
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return r

    def get_next_token(self):
        token = self.tokens[self.current_token]
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return token

    def collect_raw_result(self, queries):

        rs = (grequests.get(q,
                            headers={
                                'Authorization': 'token '
                                + self.get_next_token()
                            }
                            ) for q in queries
              )

        raw_results = grequests.imap(rs, exception_handler=exception_handler)

        try:

            raw_results = list(
                map(lambda r:
                    # print_json(r.json()["items"]),
                    r.json()["items"],
                    raw_results
                    )
            )
        except KeyError:
            print("There was a Key Error")
        raw_results = flatten(raw_results)
        res_urls = (grequests.get(response["url"],
                                  headers={
                                      'Authorization': 'token '
                                      + self.get_next_token()
                                  }
                                  ) for response in raw_results
                    )

        res_urls = grequests.map(res_urls,
                                 exception_handler=exception_handler)

        raw_results_with_url = []

        for i in range(len(raw_results)):
            ru = res_urls[i].json()

            download_url = ""
            if "download_url" in ru:
                download_url = ru["download_url"]

            raw_results_with_url.append(
                {
                    **raw_results[i],
                    **{"known_raw_url": download_url}
                }
            )

        print("Raw Results collected")
        return raw_results_with_url

    def construct_queries(self) -> list:
        return [
            "https://api.github.com/search/code?"
            + "q="
            + pattern.symbol
            + "+Donation"
            + "&page="
            + str(page)
            + "&per_page="
            + str(self.per_page)
            for pattern in self.patterns
            for page in range(0, self.max_page)
        ]

    def extract_content(self, responses) -> str:

        download_urls = (grequests.get(response["known_raw_url"],
                            headers={
                                'Authorization': 'token '
                                                 + self.get_next_token()
                            }
                           ) for response in responses
                    )

        file_contents_request = grequests.map(download_urls,
                                  exception_handler=exception_handler)

        file_contents = list(
            map(lambda f:
                "" if f is None else f.text,
                file_contents_request
                )
            )

        return file_contents

    def build_answer_json(self, item, content, symbol_list, wallet_list):

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
            "wallet_list": wallet_list
        }
        return final_json_element


pass

# gwc = GithubWalletCollector("../format.json", "../API_KEYS/login.json")
# result = gwc.collect_address()
# print_json(result)
