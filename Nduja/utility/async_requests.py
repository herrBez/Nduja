import grequests
import requests
from requests import Response
from grequests import AsyncRequest
from typing import Optional, Callable, Any, Iterable, List


def exception_handler(request : AsyncRequest, exception: Exception) -> Any:
    """Default exception handler for async request. It simply
    print an exception"""
    print(exception)


def async_requests(urls: Iterable[str],
                   ex_handler:
                   Optional[Callable[[AsyncRequest, Any], Response]]=None)\
                   -> List[Response]:
    """Given a list of urls it performs asynchronous requests"""
    rs = (grequests.get(q) for q in urls)
    if ex_handler is None:
        ex_handler = exception_handler
    return grequests.map(rs, exception_handler=ex_handler)
