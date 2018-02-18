import sys
import datetime
from typing import Optional

import requests

from requests import Response
from requests.exceptions import ReadTimeout
import logging
import pause
from utility.print_utility import print_json

from time import sleep


def perform_github_request(query: str, token: str, max_retries: int= 5) \
        -> Optional[Response]:

    retries = 0
    response = None
    while retries < max_retries:
        try:
            response = requests.get(query,
                                    headers={
                                        'Authorization': 'token ' + token
                                    },
                                    timeout=1,
                                    )
            break
        except (ConnectionError, TimeoutError, ReadTimeout):
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
