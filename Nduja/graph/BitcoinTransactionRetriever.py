
# N.B. In the bitcoin.info there are transactions that contains errors,
# therefore we should treat this kind of errors in the main loop
#
# https://blockchain.info/tx/
# d553e3f89eec8915c294bed72126c7f432811eb821ebee9c4beaae249499058d
import logging
from typing import Dict
from typing import List
from typing import Any
from typing import Tuple

import json
import requests
from graph.graph_builder import CurrencyGraph

class BtcTransactionRetriever:
    """This class is responsible for collecting the transactions of a given
    address
    """

    BITCOININFO = 'https://blockchain.info/rawaddr/'

    def address_search(self, address: str) -> \
            Dict[str, Tuple[List[str], List[str]]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        r = requests.get(BtcTransactionRetriever.BITCOININFO + address)
        raw_response = r.text

        in_out = {}  # type: Dict[str, Tuple[List[str], List[str]]]

        try:
            resp = json.loads(raw_response)  # type: Dict[str, Any]

            txs = resp["txs"]  # type: Any

            for t in txs:
                out_addr = {}  # type: Dict[str, int]
                in_addr = {}  # type: Dict[str, int]

                for o in t["out"]:
                    try:
                        e = o["addr"]
                        if e in out_addr:
                            out_addr[e] = out_addr[e] + o["value"]
                        else:
                            out_addr[e] = o["value"]

                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One output address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this output")

                for i in t["inputs"]:
                    try:
                        e = i["prev_out"]["addr"]
                        if e in in_addr:
                            in_addr[e] = in_addr[e] + i["prev_out"]["value"]
                        else:
                            in_addr[e] = i["prev_out"]["value"]
                    except KeyError:
                        logging.error("Corrupted content in bitcoin api:"
                                      + "One input address in transaction: "
                                      + t["hash"]
                                      + " is not valid. Skip this input")

                in_addr_items = in_addr.items()
                out_addr_items = out_addr.items()

                if address in in_addr_items and address in out_addr_items:

                    logging.warning("In btc transaction " + t["hash"] + " " +
                                    address + " is in both input and output")

                tmp = [(i1[0], i1[1], o1[0], o1[1], t["hash"])
                       for i1 in in_addr_items
                       for o1 in out_addr_items]

                in_out[t["hash"]] = ([i1[0] for i1 in in_addr_items],
                                     [o1[0] for o1 in out_addr_items])

        except ValueError:
            return {}

        return in_out

    def get_input_output_addresses(self, address: str) -> \
            Tuple[Dict[str, int],  Dict[str, int], Dict[str, int]]:
        """Given an address it returns ALL transactions performed
        by the address"""

        r = requests.get(BtcTransactionRetriever.BITCOININFO + address)
        raw_response = r.text

        inputs_dict = {}  # type: Dict[str, int]
        outputs_dict = {}  # type: Dict[str, int]
        connected_dict = {}  # type: Dict[str, int]

        resp = json.loads(raw_response)  # type: Dict[str, Any]

        txs = resp["txs"]  # type: Any


        for t in txs:
            out_addr = {}  # type: Dict[str, int]
            in_addr = {}  # type: Dict[str, int]

            tmp_inputs_list = []
            tmp_outputs_list = []


            for o in t["out"]:
                try:
                    e = o["addr"]
                    tmp_outputs_list.append(e)
                    out_addr[e] = 1
                except KeyError:
                    logging.error("Corrupted content in bitcoin api:"
                                  + "One output address in transaction: "
                                  + t["hash"]
                                  + " is not valid. Skip this output")

            for i in t["inputs"]:
                try:
                    e = i["prev_out"]["addr"]
                    tmp_inputs_list.append(e)
                    in_addr[e] = 1
                except KeyError:
                    logging.error("Corrupted content in bitcoin api:"
                                  + "One input address in transaction: "
                                  + t["hash"]
                                  + " is not valid. Skip this input")

            if set(tmp_outputs_list).intersection(set(tmp_inputs_list)):
                with open("suspect_transactions.txt", "a") as myfile:
                    myfile.write("===\n")
                    myfile.write(t["hash"] + "\n")
                    myfile.write("===\n")

            if address in tmp_outputs_list:
                for a in in_addr:
                    if a in inputs_dict:
                        inputs_dict[a] += 1
                    else:
                        inputs_dict[a] = 1

            if address in tmp_inputs_list:
                for a in out_addr:
                    if a in outputs_dict:
                        outputs_dict[a] += 1
                    else:
                        outputs_dict[a] = 1

            if address in tmp_inputs_list:
                for a in in_addr:
                    if a != address:
                        if a in connected_dict:
                            connected_dict[a] += 1
                        else:
                            connected_dict[a] = 1

        return inputs_dict, outputs_dict, connected_dict




# Usage example
# c = BtcTransactionRetriever()
#
# l1 = ["1CXEo9yJwU5V3d6FmGyt6ni8KFE26i6t8i","12tZFZL2Fcw5d5NyvHG35oK6tLwEjCfNhN","1B2j7DcFBC7Bp3zhMDMSC1FYLeRS9V3NVo", "1GBFh2XS2WH86dsV7BBXxFTRz6bPuQsYET"]
# l2 = ["1MVpQJA7FtcDrwKC6zATkZvZcxqma4JixS","1jc3V3T5mefuD9asa7en976NKVGssQuMq","1GBFh2XS2WH86dsV7BBXxFTRz6bPuQsYET","1aQURHDuebbJEbpBQxkWRAdW8TX8ofU17","1JmSAD7dzJjFasH7Qc3ePQACyAGbodyHry","1M9zLJveSTkoSYz1h5CWHUgo4sHijvPvjX","1CXEo9yJwU5V3d6FmGyt6ni8KFE26i6t8i","12tZFZL2Fcw5d5NyvHG35oK6tLwEjCfNhN","1B2j7DcFBC7Bp3zhMDMSC1FYLeRS9V3NVo","178rwCzpPPAcA14WdiCCRsJZLYgVwSrwSy","16GJTU4FFu5oNBJhXG7iYAf6DMAjeKiH8d","1NHAuW1Wt3DmiAxDLcK9kYw9NkeapAZ6oV","3DPD7z66T7DXULvFZUsc4xNcVS2q68TM3u","1CqSD9rxdQnKEwzqqbLwpgwCeQikFCifPj","1M72Sfpbz1BPpXFHz9m3CdqATR44Jvaydd","36XTMVtgJqqNYymsSvRonpUsbZRGkm1jvX","168NnMnmMB811ijSffpceMjTz5mg7TRZCr","168zdkYPAqMjwjior2GRyfbo1djBJL9LTH","1XPTgDRhN8RFnzniWCddobD9iKZatrvH4","1PC9aZC4hNX2rmmrt7uHTfYAS3hRbph4UN","1CiGEcAs2pXmXXeTspccFVRmvUtPuiF2CV","12CbZWfSB5TESmFwiYs4WJRZtJyi9hBPNz","33RmVRfhK2WZVQR1R83h2e9yXoqRNDvJva","122MeuyZpYz4GSHNrF98e6dnQCXZfHJeGS","1H9uAP3x439YvQDoKNGgSYCg3FmrYRzpD2","1Cc5TUgLFUF2FtjEkTc5Fxh9egTVb5tidh","17LGpN2z62zp7RS825jXwYtE7zZ19Mxxu8","1MFH5dY85Ve4Q6KYPGJnfPmiHP2UxmXend","16xpWzWP2ZaBQWQCDAaseMZBFwnwRUL4bD","1Es9qssB7275Wf9x9A21aPf8xf9wYomfv1","3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r","1HQ3Go3ggs8pFnXuHVHRytPCq5fGG8Hbhx","1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF","1L5ZQvqoeYY2WAGpwAkgd7f72fkHzLZ24Z","1NBakuExebh2M9atfS3QuSmRPPtYU398VN","1D1m9mRHegmBZnqqUVMZPauqaUqvhQfgod","1ABvtcK7neZXeQiyX2EPEo14zhhwLgphWZ","1QDwdLPrPYSoPqS7pB2kGG84YX6hEcQ4JN","1SoMGuYknDgyYypJPVVKE2teHBN4HDAh3","19Ncqupd3K2bUvNiAi6LQDLRBNpkwuGoYk","14VWYvbHd4R7oTFS8kEfoWZFTzbedDgwKg","19Ap5eTzST8AkmHXbdZoSJKmyztRXEy26p","1GDyu58t5boJVfQeC4UdB5gzh513NDZsMw","3JDkXDcc4AqzP1sUChTyte33RGCBVjqECm","3L64kHSvfPiNMkyxCKwsrWkQ5S8VMZEk1S","1K9zXU3qoGaWYocJjPqygJrLvMcyrnaC1D","1FSEEG2ZFULP51C1XBxEeyDF6Hj5A2sUaH","1NoCAhu4dYxi162srrKzi5qZiQrERuu7A4","1Dice1cF41TGRLoCTbtN33DSdPtTujzUzx","1DiceoejxZdTrYwu3FMP2Ldew91jq9L2u","1Dice1FZk6Ls5LKhnGMCLq47tg1DFG763e","1Dice2wTatMqebSPsbG4gKgT3HfHznsHWi","1F2qQL5TsLzngxQpNg88XKSnSdKKje8GBi","1LLqMFskaSaZ3w2LuH6dbQaULcy1Bu1b2R","1BkoHW3KF8E7qmUQ1xgpfPVd7BokEGozoQ","12C4Ua3zZHJWMyuZ4MTUZaZm3KPNFgo69A","1AMQg6m9GPDN9HGuC3wJGpSuiZr1XQXjxi","15fkPTtN8cRXD3moKWDoXjuiTaS9FgA3UE","17PPTHmS8N34KYKdDc4Gn1psabteGS8EE3","1TPiDevCuXc1aTLJYw3E9HVuhWnkWGJoK","195jHGYxZyYxxHAYgLVGY2H9DEoGMHGQTx","13bteFH6V2s4BqBRVYJLUUKWHK2A2PTJTb","1LKwyLK4KhojsJUEvUx8bEmnmjohNMjRDM","1LRtJBNQm9ALYt9gQjVK1TdRyQ6UPGUNCw","1N7XxSvek1xVnWEBFGa5sHn1NhtDdMhkA7","3D1YpQirXKZGn7ydnh6oUPWzo5WC4sd4Nc","1KRotMnQpxu3sePQnsVLRy3EraRFYfJQFR","1BRUcdAdjdQoAgUwcN7nbNDzqhL92ub3xE","1KEZ8V6k1Y3sk1YgKjgabhbhhdk6R5TTi8","3FzmW9JMhgmRwipKkNnphxG73VPQMsYsN6","1AVMHnFgc6SW33cwqrDyy2Fug9CsS8u6TM","3LwsJAzPd8weD1FypVWmkDFMwA7rgjPSif","15Jqeqcd9j6ftvpid5wQt9jgwCFPwuraSX","13dw6aBybHmAHFsy1ndUwWembGNzzPSE9s","3Au8ZodNHPei7MQiSVAWb7NB2yqsb48GW4","1HNeqi3pJRNvXybNX4FKzZgYJsdTSqJTbk","3A1hmUUqCUV7SdftvVpWc8jQ3xmGqBPGeZ","116Dm3aqgHNguYWbXSvPaEKe74efEkLxtu","39uk9zwu4p2JdwHXduKvVXmfJb96qwv69f","1C2gZ5apiqitgXwXVE1RPYgNj3GZHgZNk6","16rJ49uNKCohVhHvWNganP6Y48Ba9BTyKd","12YvJdkuFarTLqeaomPCXxBW9xEXd88m6K","1DKj3yeJrMShP8MdnKpTTG8TKb7ymaFN1p","14barGgijZmvXAKwMDrQLjChfKuwtnfCfW","1PHjvXGqqvZXHUtieJsfLxtBGckfT6RMbd","3DHhT6c2BN86Tx6D2w615UUSFvUwT41jY7","1EWjBTuNdfJJU2njNSyVpwGkw2s5Vm5XoN","1762SZmNRVLBYatJwdVJ9Wt3oHjj6NGjjM","1wcwG1avR4RTWoKHJDvCpffqN2gAa3VP3","1BU7wKB7DLrGqy7DEJUhTBoZtq1Qpwp6o9","14Zw65JLBgEfTyssLwfEFpU2H9ep828vPN","3JHnCcrzgUNZiud9W38joMowgh56fEbsCW","1JRY7TNYdrexWx1E7tdSrgvtNgQwssskmw","138dzurFuavqyytobDTeMhSj2gh48uadcs","1Jy3VvU9bKDotaaVy4ccLrBEEcr69CV1yX","32o6kbgZqJ9nhT2aRsfEGcMtpThJ2za89T","15gdw8khnhEvVEEjbSR8aXSPvbwNdCUEPJ","1KYogczTzDR6UX8emeEF3J76omiLqZQUff","163Bu8qMSDoHc1sCatcnyZcpm38Z6PWf6E","15ZcBgrLnjXsHGCv7iiVcxhCf9xK9xQu4B","1NiNja1bUmhSoTXozBRBEtR8LeF9TGbZBN","1Coq3qrShpWQNZ7yGCREo6EqUCdem4EdtJ","13hCzSND2hpa1UXWkc3uujgH1CwN59EKnd","151y3kWMTV5ng8wU8PupsyBnc2N66vWPTT","13TRVwiqLMveg9aPAmZgcAix5ogKVgpe4T","1BmEdTQwHHsg3DAEPQG8szPL2TeWcbA78J","15WnvJt7GCasvWuntB6AJSwVfuG7p5r7Ev","3JqsZhBnPbUvaEcTz6opfSFwddYu1YqBvt","1Price4EGW8R59auccATvEwCFAhXYBML6V","16UoC4DmTz2pvhFvcfTQrzkPTrXkWijzXw","17aGuzA9p1ZmG49V9GmR6UgGzg1dQx9We9","1Bzc7PatbRzXz6EAmvSuBuoWED96qy3zgc","1PHuSWfuAwR6oz9qV93rTdMVozfM85Qqxx","1A8JiWcwvpY7tAopUkSnGuEYHmzGYfZPiq","1CTiNJyoUmbdMRACtteRWXhGqtSETYd6Vd","1H2BHSyuwLP9vqt2p3bK9G3mDJsAi7qChw","34tLwmnGzH3gnnZZ9p2GMduXDmxr6tKEkV","1Ba8iTkxYANDjhFAvYXBaxz3EpYMVCJ6RG","18xgGTTzZU9etyBt5wC8gS2tKn5No33jw3","1GJjdX1Qkf9ZLmn13zjg8ske7uho6tSJxf","1DDrg2qEsNcB1ZwHN3U2NSz3kXvwViu1Vz","1GcN4FSHaDizu2hmtnsmjduZ2dBoJWej5E","1NVH5ub3tSw2wXaEiTXVGorMLAqhZTRAxf","13Ukb2rRTwxGk4R1upn1cPvGa1pa6vpEZe","1FkkWv8wQqJBWUcRCZkd73D8pAsykxCGNM","3GakuQQDUGyyUnV1p5Jc3zd6CpQDkDwmDq","1294cWsAYfKMTeGTYTo6egVYTk7bX7GaCv","1B1uB4Z4GoxejicoVs9c61S3jXx7BoHYDq","1NCSLjLmPyQpEHyktmUXv4WHHhnTNaJRZc","1DxBqcsspjwZ2DS5UJKpAtQb8idGgE4a8K","1GsBUQCNLdphxhuX6aZ7QAJjpnMq8MF6p8","1PZmMahjbfsTy6DsaRyfStzoWTPppWwDnZ","1FRCJoeWXbYe47cmuW3do8VoqAr9HuWbpJ","19WRmGTX417vzAu2bv65QicNj54QMVn1qF","1ASsGfGXXVzeh1ExwzaFLPjTTT11rq2PzN","19vdDaxZsfqF8SJAcE2zZNa7sAWSiQyfxa","1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX","17QnVor1B6oK1rWnVVBrdX9gFzVkZZbhDm","1387fFG7Jg1iwCzfmQ34FwUva7RnC6ZHYG","14WTbezUqWSD3gLhmXjHD66jVg7CwqkgMc","15Z2Goc47t4vQvRL22n8x6qC43JgH97VGE","3Qn9tMvDi3bV5sySg9zbwZ5kNixh8vzwaq","3H1iYwKhS3QtebfEE5xysouWzm924rdM9i","1CMZNs2nQjkfvit8Qoq1ZL38XUPJ6EDwCu","1FpxPPXXonXudUbid1GbXmBuhBoRQU7agT","1D1ZrZNe3JUo7ZycKEYQQiQAWd9y54F4XZ","171sgjn4YtPu27adkKGrdDwzRTxnRkBfKV","1NLkGPnNbT9iCJ35U9UfsURANtYgNREVtq","16wPejzMfbTARNJBoYcTFwHqUKVVKXYSYS","11r118H2Qv4oHfjFuJnuU8GZHGNqwEH9e","1HAyTwtxMEkJaHdUYMXVvoXp2PHgwFx2M9","1MQS2nyvjFyqDjybiaz9KBdfxAFcsyDg87","1NsnsnqkkVuopTGvUSGrkMhhug8kg6zgP9","1EY5WbiW3YkWanSKEGcjCETpQfCR81wc56","1TipsGocnz2N5qgAm9f7JLrsMqkb3oXe2","13PnEKpfVzNseWkrm6LoueKcCMPj74zPv7","1JAFefdPVAs3WQiTqnYWbsjifJAEjQcjQ8","1HWpyFJ7N6rvFkq3ZCMiFnqM6hviNFmG5X","1Mwi6dWzuBKBeM4Gy7sHGLbiRB35W1SqA3","3EktnHQD7RiAE6uzMj2ZifT9YgRrkSgzQX","1RustyRX2oai4EYYDpQGWvEL62BBGqN9T","14qNSyVPtFh4twWLD7f5nuosb2MZCxcuPh","1KAf7dFEio5X9HS5Qv9SM9Z7484Mf7jNHm","1MCYaBkdQskbZJXYBmK4QkxUsWxuaXXaDh","1CKY9w39ixKkjKh9stYeAfxm3whFazQRbJ","19jSqVd8bpevi3qacBedkAdDqEXtGAn5t7","1JVPjWF9igFFzSdYCSegpWZX2XdJv3p945","1MEWT2SGbqtz6mPCgFcnea8XmWV5Z4Wc6","1PaH4UJpw8UxLBV5adLN3nR9kkDCw2bd2h","1LESkkWa131rAJpFsdHdRmUT8PT63Yis1R","1TobyaXFetqBigGb7zRrLbMXLzUnsrrQA","1FNAUDMhAD3d6uHahVcXBZrTdsX7NZyYCf","17gbJUL2Mi9McuM7J3FBW9ddyYyT6hLpX9","1HpdeZ3fR234fCau77JtMdnQNGUe6iHHu6","14JkMR68n4PBASB3TgvpjtaPTbfffSwFbW","1CWHWkTWaq1K5hevimJia3cyinQsrgXUvg","1JWVN1d9MJGUMTcqd2dDd5KWuhw7GsMGSe","3FopcPnDHXcR83qyMUyt5gE9u3WXkxgVUs","1PUNRsv8vDt1upTx9tTpY5sH8mHW1DTrKJ","1EMA2fGRyX5UuA4azcVjmTkc1Bkpq3UBXP","1AZYKstEvRLhYnQCheYutqyZ5oNS4SwoJw","1EDGSgTW5iGHGesyYACSXYUNbwB6BPEDan","14MEpy5a9MwDZa9CUzrfDhTU8dy2KKJ5mU","1ECXwPU9umqtsBAQesBW9981mx6sipPmyL","1Bu3bhwRmevHLAy1JrRB6AfcxfgDG2vXRd","1PEoUKNxTZsc5rFSQvQjeTVwDE9vEDCRWm","19jhbHzRZR1Veh956p9eC2FKupvxXUAYT","1XeRocJ6PRUX419QQo9crW5nbsjetJLUn","1AiT1j185rZ7cokrGrszZJLWAktaFszCUR","1BjEJBytssDg6WpCnYDc9ini5ecZevJ3Q","1CZDM6oTttND6WPdt3D6bydo7DYKzd9Qik","12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjrJX","19Vqc8uLTfUonmxUEZac7fz1M5c5ZZbAii","17WFx2GQZUmh6Up2NDNCEDk3deYomdNCfk"]
#
# l = ["17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"]
#
# g = CurrencyGraph()

# g = CurrencyGraph(l)
# for addr_id in range(len(l)):
#
#     addr = l[addr_id]
#
#     print("Analyze " + addr + " " + str(addr_id + 1) + "/" + str(len(l)) + " " +
#           str((addr_id+1)/len(l)*100) + "%"
#           )
#
#
#     addr, tr = c.address_search(addr)
#
#     for (i, o, h) in tr:
#         g.add_edge(i[0], o[0], trx=h, ivalue=i[1], ovalue=o[1])
#
#     print("Finished ")
#
# print("Loaded. Now Print")
#
#
#
# g.plot_multigraph()


# print(c.address_search('1EQ1aVN4Au7adKTT6JXtSpnz75HVVNkMmp'))
# print(c.address_check("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j"))
# print(c.address_check('16hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))
# print(c.address_check('6hJF5mceSojnTD3ZTUDqdRhDyPJzoRakM'))