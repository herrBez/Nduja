from typing import Optional

import requests
from requests import Response
from requests.exceptions import ReadTimeout
from time import sleep
import json


def safe_requests_get(query: str, token: Optional[str] = None,
                      timeout: int = 120, max_retries: int = 10,
                      jsoncheck: bool = False) -> \
        Optional[Response]:
    retries = 0
    response = None  # type: Optional[Response]

    if token is not None:
        headers = {
                                        'Authorization': 'token ' + token
                                    }
    else:
        headers = None

    while retries < max_retries:
        try:
            response = requests.get(query,
                                    headers=headers,
                                    timeout=timeout,
                                    )
            if jsoncheck:
                json.loads(response.text)
            break
        except (ConnectionError, TimeoutError, ReadTimeout):
            retries += 1
            response = None
            sleep(2)
        except Exception:
            retries += 1
            response = None
            sleep(10)


    return response