# This is a stub for the pause module. It contains only the functions
# used in Nduja. It is **not complete**

from typing import Any
from typing import Iterable
from typing import List
from typing import Callable
from typing import Optional
from requests import Response

class AsyncRequest(object): ...

def get(q : str, **kwargs: Any) -> AsyncRequest: ...

def map(reqs: Iterable[AsyncRequest],
        exception_handler: Optional[Callable[[AsyncRequest, Any], Response]]= None) -> List[Response]: ...