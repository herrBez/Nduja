import json


class Parser:
    def parse(path):
        results = json.load(open(path))
        noDuplicate = []
        for res in results["results"]:
            if res not in noDuplicate:
                noDuplicate.append(res)
        for res in noDuplicate:
            print(res["username"] + "|" + res["url"])
