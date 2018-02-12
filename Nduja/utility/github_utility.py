import grequests
import requests
from grequests import AsyncRequest
from requests import Response
import logging
import pause

from typing import Iterable
from typing import List
from typing import Callable


def default_github_exc_handler(request: AsyncRequest,
                               exception: Exception) -> Response:
    """Exception handler for the github grequest. It simply retry
    the failing request once and on success return the new response
    otherwise it gives up and gives back a None."""

    logging.warning("error with request. Trying to avoid None")
    response = grequests.map([request])
    if response[0] is None:
        logging.error("Retried. But Failed")
        logging.error(str(exception))
    else:
        logging.info("Retried successfully")
    return response[0]


def perform_request(rs: Iterable[AsyncRequest],
                    exception_handler: Callable =
                    default_github_exc_handler) -> List[Response]:

    # transform the iterable into a list
    async_request_list = list(rs)  # type: List[AsyncRequest]

    # try to get all async requests
    raw_results = grequests.map(async_request_list,
                                exception_handler=exception_handler)

    reset_time = -1
    while None in raw_results:
        # Find one valid result to pause until the reset time
        for i in range(len(raw_results)):
            r = raw_results[i]
            if r is not None:
                logging.warning("Sleep Until "
                                + dict(r.headers)["X-RateLimit-Reset"])

                # It is very unlikely that that we find different
                # X-RateLimit-Reset --> but we want to be safe
                reset_time = max(reset_time,
                                 int(dict(r.headers)["X-RateLimit-Reset"]))
                pause.until(reset_time)
                break  # Wait only once

        # get the requests for which the result is None
        tmp_requests = []  # type: List[AsyncRequest]

        # Create a stack of async requests that failed
        for i in range(len(raw_results)):
            if raw_results[i] is None:
                tmp_requests.append(async_request_list[i])

        # retry to get the failed requests
        tmp_raw_result = grequests.map(tmp_requests,
                                       exception_handler=exception_handler)

        # Pop from the results of the retried requests
        for i in range(len(raw_results)):
            if raw_results[i] is None:
                raw_results[i] = tmp_raw_result.pop(0)

    return raw_results
