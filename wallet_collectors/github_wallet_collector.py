import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from wallet_collectors.abs_wallet_collector import Pattern
import sys
import grequests
import requests
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep
import pause
import math

def print_json(s):
    print(json.dumps(s, indent=2))

def exception_handler(request, exception):
    print("error with request")
    print(exception)


class GithubWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens):
        super().__init__(format_file)
        self.format_object = json.load(open(format_file))
        self.max_page = 30
        self.per_page = 100
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
        sleep(20)
        raw_results_with_url = []

        max_index = 0
        try:
            # We proceed sequentially to avoid to be blocked for abuses of
            # api.
            while max_index < len(queries):
                min_index = max_index
                max_index = min(max_index + len(self.tokens),
                                len(queries))
                rs = (grequests.get(q,
                                    headers={
                                        'Authorization': 'token '
                                        + self.get_next_token()
                                    }
                                    ) for q in queries[min_index:max_index]
                      )

                raw_results = grequests.map(rs, exception_handler=exception_handler)

                for r in raw_results:
                    # print_json(json.loads(r.headers))
                    # print("Remaing calls: "
                    #       + str(dict(r.headers)["X-RateLimit-Remaining"])
                    #       )
                    if int(dict(r.headers)["X-RateLimit-Remaining"]) <= 1: # Let's wait until
                        print("Let's pause 'cause we do not have rate")
                        pause(dict(r.headers)["X-RateLimit-Reset"])

                # Filter out None responses
                raw_results = [r for r in raw_results if r is not None]

                raw_results = list(
                    map(lambda r1:
                        # print_json(r.json()["items"]),
                        r1.json()["items"],
                        raw_results
                        )
                )

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


                for i in range(0, len(res_urls)):
                    # print_json(raw_results[i])
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
                                **raw_results[i],
                                **tmp
                            }
                        )
                    else:
                        print(str(i) + " res_url is None")

        except KeyError:
            print("There was a Key Error")

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
        # for response in responses:
        #     print(response["known_raw_url"])

        print("Hallo")

        download_urls = (grequests.get(response["known_raw_url"],
                            headers={
                                'Authorization': 'token '
                                                 + self.get_next_token()
                            }
                           ) for response in responses
                    )

        file_contents_responses = grequests.map(download_urls,
                                  exception_handler=exception_handler)


        # for fcr in file_contents_responses:
        #
        #     print("text" + fcr.text)
        #     # print("content" + fcr.content.decode()
        #     # print("raw" + fcr.raw)
        #     sleep(10)


        file_contents = list(
            map(lambda f:
                "" if f is None else f.text,
                file_contents_responses
                )
            )


        return file_contents

    def build_answer_json(self, item, content, symbol_list, wallet_list, emails,
                          websites):

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
