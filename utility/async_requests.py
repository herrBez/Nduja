import grequests
import requests


def exception_handler(request, exception):
    """Default exception handler for async request. It simply
    print an exception"""
    print(exception)


def async_requests(urls, ex_handler=None):
    """Given a list of urls it performs asynchronous requests"""
    rs = (grequests.get(q) for q in urls)
    if ex_handler is None:
        ex_handler = exception_handler
    return grequests.map(rs, exception_handler=ex_handler)
