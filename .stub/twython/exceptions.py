class TwythonError(Exception):
    @property
    def msg(self) -> str: ...

class TwythonRateLimitError(TwythonError):
    @property
    def retry_after(self) -> int: ...