from typing import Generator, Optional, Any, List


class Process(object):
    def name(self) -> str: ...
    def cmdline(self) -> List[str]: ...


def process_iter(attrs: Optional[Any] = None,
                 ad_value: Optional[Any] = None) \
        -> Generator[Process, Any, Any]: ...