import grequests
import requests
from grequests import AsyncRequest
from requests import Response
from time import sleep
import logging
import pause

from typing import Iterable
from typing import List
from typing import Callable


def default_github_exc_handler(request: AsyncRequest,
                               exception: Exception) -> Response:
    """Exception handler for the grequests map function. It simply retry
    the failing request once and on success return the new response
    otherwise it gives up and gives back a None"""

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

    raw_results = grequests.map(rs,
                                exception_handler=exception_handler)

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
