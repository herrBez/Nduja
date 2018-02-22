import sys
import datetime
import requests

from requests import Response
from requests.exceptions import ReadTimeout
import logging
import pause
from utility.print_utility import print_json
from utility.safe_requests import safe_requests_get
from time import sleep


def perform_github_request(query: str, token: str, max_retries: int= 5) \
        -> Response:

    response = safe_requests_get(query, token=token, timeout=1,
                                 jsoncheck=False, max_retries=max_retries)

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
