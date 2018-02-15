import sys
import datetime
import grequests
import requests
from grequests import AsyncRequest
from requests import Response
import logging
import pause
from utility.print_utility import print_json

from time import sleep
from typing import Iterable
from typing import List
from typing import Callable


def perform_github_request(query: str, token: str, max_retries:int = 5)\
    -> Response:

    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(query,
                                    headers={
                                        'Authorization': 'token ' + token
                                    },
                                    timeout=300,
                                    )
            break
        except ConnectionError:
            retries += 1
            sleep(2)
        except TimeoutError:
            retries += 1
            sleep(2)

    if response is not None:
        try:
            remaining_calls = int(dict(response.headers)["X-RateLimit-Remaining"])
        except KeyError:
            print(query)
            print_json(dict(response.headers))
            sys.exit(1)

        if remaining_calls < 1:
            total_calls = int(dict(response.headers)["X-RateLimit-Limit"])

            reset_time = int(dict(response.headers)["X-RateLimit-Reset"])

            next_reset_date_str = datetime.datetime. \
                fromtimestamp(reset_time) \
                .strftime('%H:%M:%S %Y-%m-%d')

            logging.warning("Rate Limit reached (/"
                            + str(total_calls)
                            + ": Pause until: "
                            + next_reset_date_str)

            pause.until(reset_time)

    return response
