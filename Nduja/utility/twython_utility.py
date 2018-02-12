import datetime
import json
import logging
from time import sleep

# import grequests
# import requests
import pause
from twython import Twython
from twython.exceptions import TwythonError
from twython.exceptions import TwythonRateLimitError
from twython.exceptions import TwythonAuthError
from utility.print_utility import print_json


from typing import Any
from typing import Dict
from typing import Callable
from typing import Optional


def twitter_safe_call(twython_function: Callable[..., Any],
                      max_retry_on_error: int = 5,
                      **params: Any) -> Optional[Dict]:
    """This utility function calls a twython function safely, by catching
    the exceptions that can rise:
    if a TwythonRateLimitError occurs, it pauses until the reaching of the
    next release date and retries
    if a TwythonError occurs, it sleeps 1 minute and retry max_retry_on_error
    times. If the number of replies is exceeded it returns an empty dictionary
    """

    retry_on_error = 0
    result = None  # type: Dict

    while True:
        exception_raised = False

        try:
            logging.debug("Try" + json.dumps(params))

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
        except TwythonAuthError as tae:
            logging.warning("Twython Authorization error raised: " + tae.msg)
            logging.warning("The query was: " + json.dumps(params, indent=2))
            sleep(10)
            return None
        except TwythonError as te:
            retry_on_error += 1
            logging.warning("TwythonError raised: " + te.msg)
            print_json(params)
            sleep(2)
            exception_raised = True
            if retry_on_error > max_retry_on_error:
                with open("suspended.txt", "a") as myfile:
                    myfile.write("===")
                    myfile.write(str(twython_function))  # print the type of fun
                    myfile.write(te.msg)  # the error message
                    myfile.write(json.dumps(params))  # print the params
                    myfile.write("===")
                return None

        if not exception_raised:
            break

    return result
