import requests
import json
from queue import Queue

# 定义请求头
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}


# 获取所有的collections
def get_collections(que: Queue):
    url = "https://api-mainnet.magiceden.io/all_collections"
    response = requests.get(url=url, headers=headers)
    data = response.json()["collections"]
    if data:
        # 添加到队列当中
        for d in data:
            que.put((d["symbol"], d["name"], d["description"]))


# 查询详细信息
def query_detail(collection: tuple, data_list: list):
    url = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery"
    query = {"$match": {"collectionSymbol": collection[0]}, "$sort": {"createdAt": -1}, "$skip": 0, "$limit": 1000}
    params = [
        ("q", json.dumps(query))
    ]
    # print(params)
    response = requests.get(url=url, headers=headers, params=params)
    # print(response.text)
    data = response.json()["results"]
    # listings
    listings = []
    result = dict()
    for d in data:
        data_dic = dict()
        data_dic["title"] = d["title"]
        data_dic["currentPrice"] = d["price"]
        data_dic["img"] = d["img"]
        listings.append(data_dic)
    # 组装成 {"collection": collection, "description": description, "listings": listings}格式
    result["collection"] = collection[1]
    result["description"] = collection[-1]
    result["listings"] = listings
    print(listings)
    # 保存结果
    data_list.append(result)


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
        query_detail(element, data_list)
    # 写入文件
    print(data_list)
    with open('./result.json', 'w', encoding='utf_8_sig') as wf:
        json.dump(data_list, wf)


if __name__ == '__main__':
    main()
