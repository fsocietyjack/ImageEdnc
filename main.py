import requests
import json
from queue import Queue
from fake_useragent import UserAgent
from time import sleep
import simplejson

# 定义请求头
headers = {
    "user-agent": UserAgent().random,
    "referer": "https://magiceden.io/",
    "accept-language": "zh,en-US;q=0.9,en;q=0.8",
    "accept": "application/json, text/plain, */*"
}
session = requests.Session()


# 获取所有的collections
def get_collections(que: Queue):
    url = "https://api-mainnet.magiceden.io/all_collections"
    response = session.get(url=url, headers=headers)
    data = response.json()["collections"]
    if data:
        # 添加到队列当中
        print(len(data))
        for d in data:
            que.put((d["symbol"], d["name"], d["description"]))


# 查询详细信息
def query_detail(que: Queue, collection: tuple, data_list: list):
    url = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery"
    query = {"$match": {"collectionSymbol": collection[0]}, "$sort": {"createdAt": -1}, "$skip": 0, "$limit": 500}
    params = [
        ("q", json.dumps(query))
    ]
    try:
        # print(params)
        response = session.get(url=url, headers=headers, params=params)
        # print(response.text)
        data = response.json()["results"]
        # 判断是否是返回 Your limit exceed
        if isinstance(data, str):
            print('次数限制...', data)
            que.put(collection)
            return
        # listings
        listings = []
        result = dict()
        for d in data:
            data_dic = dict()
            data_dic["title"] = d["title"]
            data_dic["currentPrice"] = d["price"]
            try:
                data_dic["img"] = d["img"]
            except KeyError:
                data_dic["img"] = ""
            try:
                data_dic["escrowPubkey"] = d["escrowPubkey"]
            except KeyError:
                data_dic["escrowPubkey"] = ""
            try:
                data_dic["mintAddress"] = d["mintAddress"]
            except KeyError:
                data_dic["mintAddress"] = ""
            try:
                data_dic["owner"] = d["owner"]
            except KeyError:
                data_dic["owner"] = ""
            listings.append(data_dic)
        # 组装成 {"collection": collection, "description": description, "listings": listings}格式
        result["collection"] = collection[1]
        result["description"] = collection[-1]
        result["listings"] = listings
        print(listings)
        print(collection)
        # 保存结果
        data_list.append(result)
    except (simplejson.errors.JSONDecodeError, requests.exceptions.ConnectionError):
        print('解析json数据错误...重新加入队列')
        que.put(collection)


def main():
    # 初始化队列
    que = Queue()
    get_collections(que)
    # 保存数据结果
    data_list = []
    # 判断队列是否为空
    while not que.empty():
        # 获取队列元素
        element = que.get()
        query_detail(que, element, data_list)
        # sleep(3)
    # 写入文件
    # print(data_list)
    with open('./result.json', 'w', encoding='utf_8_sig') as wf:
        json.dump(data_list, wf)


if __name__ == '__main__':
    main()
