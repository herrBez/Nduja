import datetime
import json
import logging
from time import sleep
# import grequests
# import requests
import pause
from twython import TwythonError
from twython import TwythonRateLimitError
from utility.print_utility import print_json

from typing import Dict


def twitter_safe_call(twython_function, max_retry_on_error: int = 10,
                      **params: Dict) -> Dict:
    """This utility function calls a twython function safely, by catching
    the exceptions that can rise:
    if a TwythonRateLimitError occurs, it pauses until the reaching of the
    next release date and retries
    if a TwythonError occurs, it sleeps 1 minute and retry max_retry_on_error
    times. If the number of replies is exceeded it returns an empty dictionary
    """

    retry_on_error = 0
    result = {}

    while True:
        exception_raised = False

        try:
            logging.debug("Try" + json.dumps(params))
            sleep(1)

            result = twython_function(
                timeout=120,  # Max Timeout 2 minutes
                **params
            )
            logging.debug("Try Done")
        except TwythonRateLimitError as tre:
            next_reset = int(tre.retry_after) + 1

            next_reset_date_str = datetime.datetime. \
                fromtimestamp(next_reset) \
                .strftime('%H:%M:%S %Y-%m-%d')

            logging.warning("Rate Limit reached: Pause until: "
                            + next_reset_date_str)

            pause.until(next_reset)

            logging.warning("Pause Finished. Let's retry")

            exception_raised = True
        except TwythonError as te:
            retry_on_error += 1
            logging.warning("TwythonError raised: " + te.msg)
            print_json(params)
            sleep(60)
            exception_raised = True
            if retry_on_error > max_retry_on_error:
                return {}

        if not exception_raised:
            break

    return result
