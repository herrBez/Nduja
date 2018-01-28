import json
from abs_wallet_collector import AbsWalletCollector
from abs_wallet_collector import Pattern


def print_json(s):
    print(json.dumps(s, indent=2))


class GithubWalletCollector(AbsWalletCollector):
    def __init__(self, format_file, login_file):
        super().__init__(format_file)
        self.format_object = json.loads(open(format_file).read())
        if not (login_file is None):
            self.login_object = json.loads(open(login_file).read())
        self.max_page = 1

    def collect_raw_result(self, query):
        a = json.loads(
            self.request_url(
                query,
                self.login_object["token"]
            )
        )

        return a["items"]

    def construct_queries(self, pattern) -> list:
        pages = [0]
        return list(
            map(lambda page:
                "https://api.github.com/search/code?q=" +
                pattern.symbol +
                "+Donation" +
                "&page=" +
                str(page) +
                "&per_page=30",
                pages
                )
        )

    def extract_content(self, response) -> str:
        res_url = json.loads(
            self.request_url(
                response["url"],
                self.login_object["token"]
            )
        )

        download_url = res_url["download_url"]
        file_content = self.request_url(
            download_url,
            self.login_object["token"]
        )
        return file_content

    def build_answer_json(self, item, content, symbol_list, wallet_list):

        final_json_element = {
            "hostname": "github.com",
            "text": content,
            "username_id": item["repository"]["owner"]["id"],
            "username": item["repository"]["owner"]["login"],
            # not sure if screen_name = username or not
            # but username is not a field
            "symbol": symbol_list,
            "repo": item["repository"]["name"],
            "repo_id": item["repository"]["id"],
            "known_raw_url": "",
            "wallet_list": wallet_list
        }
        return final_json_element


pass

# gwc = GithubWalletCollector("../format.json", "../API_KEYS/login.json")
# result = gwc.collect_address()
# print_json(result)
