import grequests
import requests


def exception_handler(request, exception):
    print(exception)


def async_requests(urls, ex_handler=None):
    rs = (grequests.get(q) for q in urls)
    if ex_handler is None:
        ex_handler = exception_handler
    return grequests.map(rs, exception_handler=exception_handler)
