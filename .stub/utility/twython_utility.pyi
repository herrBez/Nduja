from typing import Dict
from typing import Any


def twitter_safe_call(twython_function, max_retry_on_error: int = 10,
                      **params: Dict) -> Dict[str, Any]: ...