"""Module for utility function to use github API"""
from typing import Optional

import logging
import datetime
from time import sleep
import pause

from requests import Response

from utility.print_utility import print_json
from utility.safe_requests import safe_requests_get


def perform_github_request(query: str, token: str, max_retries: int = 5) \
        -> Optional[Response]:
    """Perform requests using github API"""
    is_valid = False
    while not is_valid:
        is_valid = True

        response = safe_requests_get(query, token, 5, jsoncheck=True,
                                     max_retries=max_retries)

        if response is not None:
            if response.status_code == 403:
                retry_after = int(dict(response.headers)["Retry-After"])
                sleep(retry_after + 1)
                is_valid = False

    try:
        remaining_calls = int(dict(response.headers)["X-RateLimit-Remaining"])
    except KeyError:
        print(query)
        print_json(dict(response.headers))
        return None

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
