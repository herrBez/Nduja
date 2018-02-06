# This is a stub for the pause module. It contains only the functions
# used in Nduja. It is **not complete**

from typing import Any
from typing import List
from typing import Callable

class AsyncRequest(object): ...

def get(q : str, **kwargs: Any) -> Any: ...

def map(reqs: Any,
        exception_handler: Callable[[AsyncRequest, Any], Any] = None) -> List[Any]: ...