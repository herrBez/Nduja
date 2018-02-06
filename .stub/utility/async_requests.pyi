import grequests
import requests
from requests import Response
from typing import List
from typing import Callable
from typing import Any


def exception_handler(request, exception : Callable) -> Any: ...


def async_requests(urls : List[str], ex_handler: Callable = None) -> Response: ...