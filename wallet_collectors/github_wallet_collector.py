import json
from wallet_collectors.abs_wallet_collector import AbsWalletCollector
import grequests
from wallet_collectors.abs_wallet_collector import flatten
from time import sleep
import pause
import logging
from utility.print_utility import print_json

from requests import Response
from grequests import AsyncRequest

from typing import List
from typing import Any
from typing import Dict


def exception_handler(request: AsyncRequest, exception: Exception) -> Response:
    """Exception handler for the grequests map function. It simply retry
    the failing request once and on success return the new response
    otherwise it gives up and gives back a None"""

    logging.warning("error with request. Trying to avoid None")
    # res = grequests.get(request)
    response = grequests.map([request])
    if response[0] is None:
        logging.error("Retried. But Failed")
        logging.error(str(exception))
        sleep(10)
    else:
        logging.info("Retried successfully")
    return response[0]


class GithubWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens) -> None:
        super().__init__(format_file)
        self.format_object = json.load(open(format_file))
        self.max_page = 10
        self.per_page = 100
        self.current_token = 0
        self.tokens = tokens

    def request_url(self, url: str, token: str =None) -> str:
        r = super().request_url(url, self.tokens[self.current_token])
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return r

    def get_next_token(self) -> str:
        token = self.tokens[self.current_token]
        self.current_token = (self.current_token + 1) % len(self.tokens)
        return token

    def perform_request(self, rs: Any) -> Any:

        raw_results = grequests.map(rs, exception_handler=exception_handler)

        while None in raw_results:
            logging.warning("There is a None. Let's pause?")
            for r in raw_results:
                if r is not None:
                    logging.warning("Sleep Until "
                                    + dict(r.headers)["X-RateLimit-Reset"])
                    pause.until(int(dict(r.headers)["X-RateLimit-Reset"]))
            raw_results = grequests.map(rs, exception_handler=exception_handler)

        for r in raw_results:
            if int(dict(r.headers)[
                       "X-RateLimit-Remaining"]) <= 5:  # Let's wait until
                logging.warning("Let's pause 'cause we do not have rate")
                logging.warning("Until " + dict(r.headers)["X-RateLimit-Reset"])
                pause.until(int(dict(r.headers)["X-RateLimit-Reset"]))

        return raw_results

    def collect_raw_result(self, queries: List[str]) -> List[Dict[str, Any]]:
        raw_results_with_url = []

        max_index = 0

        # We proceed sequentially to avoid to be blocked for abuses of
        # api.
        while max_index < len(queries):
            min_index = max_index
            max_index = min(max_index + len(self.tokens),
                            len(queries))

            logging.debug("Q[" + str(min_index) + ":" + str(max_index) + "] A")

            rs = (grequests.get(q,
                                headers={
                                    'Authorization': 'token '
                                                     + self.get_next_token()
                                },
                                timeout=300,
                                ) for q in queries[min_index:max_index]
                  )

            raw_results = self.perform_request(rs)

            # Filter out None responses
            raw_results = [r for r in raw_results if r is not None]

            for r1 in raw_results:
                if "items" not in r1.json():
                    print_json(dict(r1.json()))
                    sleep(30)

            raw_results = list(
                map(lambda r1:
                    # print_json(r.json()["items"]),
                    r1.json()["items"],
                    raw_results
                    )
            )

            raw_results = flatten(raw_results)
            logging.debug("Q[" + str(min_index) + ":" + str(max_index) + "] B")

            r_max_index = 0

            res_urls = [] # type: List[Response]

            while r_max_index < len(raw_results):
                r_min_index = r_max_index
                r_max_index = min(r_max_index + len(self.tokens),
                                len(raw_results))

                logging.debug(
                    "RES_URL["
                    + str(r_min_index)
                    + ":"
                    + str(r_max_index)
                    + "] A")

                tmp_res_url = (grequests.get(response["url"],
                                          headers={
                                              'Authorization': 'token '
                                              + self.get_next_token()
                                          },
                                          timeout=200
                                          ) for response in raw_results[r_min_index:r_max_index]
                            )

                res_urls = res_urls + self.perform_request(tmp_res_url)

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
                            **raw_results[i],
                            **tmp
                        }
                    )
                else:
                    logging.warning(str(i) + " res_url is None")

        logging.info("Finish Collection of Raw Results")
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
            for page in range(1, self.max_page+1)
        ]

    def extract_content(self, responses) -> List[str]:
        logging.debug("Entering extract Content")
        contents = []  # type: List[str]
        max_index = 0

        while max_index < len(responses):

            min_index = max_index
            max_index = min(max_index + len(self.tokens),
                            len(responses))

            logging.debug("R[" + str(min_index) + ":" + str(max_index) + "]")

            download_urls = (grequests.get(response["known_raw_url"],
                                           headers={
                                               'Authorization': 'token '
                                                                + self.get_next_token()
                                           },
                                           timeout=300,
                                           ) for response in
                             responses[min_index:max_index]
                             )

            file_contents_responses = \
                grequests.map(download_urls, exception_handler=exception_handler)

            file_contents = list(
                map(lambda f:
                    "" if f is None else f.text,
                    file_contents_responses
                    )
                )
            contents += file_contents

        return contents

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
