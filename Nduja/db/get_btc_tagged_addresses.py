"""This script get all the tagged address from blockchain info and save
them onto a file."""


from bs4 import BeautifulSoup
import requests
from typing import List
from time import sleep


def main() -> None:
    offset = 0

    tagged_addresses = []  # type: List[str]
    tagged_addresses_name = []  # type: List[str]
    tagged_addresses_link = []  # type: List[str]
    tagged_addresses_verified = []  # type: List[bool]

    while True:
        
        payload = {'filter': '8', 'offset': str(offset)}
        
        print(payload)
        
        response = requests.get("https://blockchain.info/tags", 
                                params=payload)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Take the second table that contains the tagged addresses
        tag_table = soup.body.findAll("table")[1]

        trs = tag_table.tbody.findAll("tr")
        if len(trs) < 1:
            print("Finish Reached")
            break
        
        for tr in trs:
            tds = tr.findAll("td")
            tagged_addresses.append(tds[0].a.text)
            tagged_addresses_name.append(tds[1].span.text)
            tagged_addresses_link.append(tds[2].findAll("a",
                                                        href=True)[0]["href"])
            tagged_addresses_verified.append(True if "green"
                                                     in tds[3].img["src"]
                                             else False)
        
        offset += 50
        sleep(1) # sleep to avoid beeing blocked


        
    print("Research has finished. Writing to file. Please do not exit")


    with open("/tmp/tagged_address_all_info.txt", "w") as out:
        for i in range(len(tagged_addresses)):
            out.write(tagged_addresses[i] + " " +
                tagged_addresses_name[i] + " " +
                tagged_addresses_link[i] + " " +
                str(tagged_addresses_verified[i]) + "\n")
            


    with open("known_addresses_btc", "w") as out:
            for i in range(len(tagged_addresses)):
                out.write(tagged_addresses[i] + "\n")
                
if __name__ == "__main__":
    main()
