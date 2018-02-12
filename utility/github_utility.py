import datetime
import grequests
import requests
from grequests import AsyncRequest
from requests import Response
import logging
import pause

from typing import Iterable
from typing import List
from typing import Callable


def perform_github_request(query: str, token: str) -> Response:
    response = requests.get(query,
                            headers={
                                'Authorization': 'token ' + token
                            },
                            timeout=300,
                            )

    if response is not None:
        remaining_calls = int(dict(response.headers)["X-RateLimit-Remaining"])
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
