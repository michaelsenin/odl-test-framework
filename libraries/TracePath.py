import collections
import requests
import json

class TracePath(object):
    def __init__(self):
        pass

    def getRequest(self, path, route):
        AUTH = ("admin", "admin")
        HEADERS = {"content-type": "application/json"}
        tx_resp = []
        rx_resp = []
        rx_count = 0.0
        tx_count = 0.0
        resp_details = []
        resp_details = route.split(',')
        for i in range(0, len(resp_details)):
            node, port = resp_details[i].split(':', 1)
            url = '{path}/controller/nb/v2/ncn/statistics/switches/{nodeId}/ports/{portId}'.format(path=path, nodeId=node, portId=port)
            response = requests.get(url, auth=AUTH, headers=HEADERS)
            resp_cont_json = json.loads(response.content)
            tx_resp.append(resp_cont_json['tx-packets'])
            tx_count = tx_count + tx_resp[i]
            rx_resp.append(resp_cont_json['rx-packets'])
            rx_count = rx_count + rx_resp[i]
        return rx_count, tx_count

    def tracePath(self, path, route):
        before_count_rx, before_count_tx = TracePath.getRequest(self, path, route)
        return before_count_rx, before_count_tx

    def checkTracePath(self, path, route, before_count_rx, before_count_tx):
        after_count_rx, after_count_tx = TracePath.getRequest(self, path, route)
        tx_delta = after_count_tx - before_count_tx
        rx_delta = after_count_rx - before_count_rx
        return rx_delta, tx_delta
