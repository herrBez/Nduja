from wallet_collectors.abs_wallet_collector import AbsWalletCollector
from typing import Any
from typing import List
from typing import Dict



class SearchcodeWalletCollector(AbsWalletCollector):

    def __init__(self, format_file, tokens) -> None: ...

    def request_url(self, url: str, token: str=None) -> str: ...

    def get_next_token(self) -> str: ...

    def perform_request(self, rs: Any) -> Any: ...

    def collect_address(self) -> str: ...

    def collect_raw_result(self, queries: List[str]) -> List[Any]: ...

    def construct_queries(self) -> List[str]: ...

    def extract_content(self, response: Dict[str, Any]) -> List[str]: ...



    def build_answer_json(self, raw_response: Dict[str, Any], content: str,
                          match_list, symbol_list, wallet_list, emails=None,
                          websites=None) -> Dict[str, Any]: ...

    def extract_content_single(self, response) -> str: ...


# swc = SearchcodeWalletCollector("../format.json")
# result = swc.collect_address()
# print(result)