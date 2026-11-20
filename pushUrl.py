import random
import re
import time

import requests
import argparse
import os

# 每日推送限额，可根据实际情况修改
QUOTA = 100


def parse_stiemap(site):
    site = f'{site}/sitemap.xml'
    try:
        result = requests.get(site, timeout=15)
        big = re.findall('<loc>(.*?)</loc>', result.content.decode('utf-8'), re.S)
        return list(big)
    except:
        print('请检查你的url是否有误。')
        print('正确的应是完整的域名，包含https://，且不包含‘sitemap.xml’, 如下所示：')
        print('正确的示例: https://ghlcode.cn')
        print('详情参见: https://ghlcode.cn/fe032806-5362-4d82-b746-a0b26ce8b9d9')



def push_to_bing(site, urls, api_key):
    endpoint = "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlbatch"

    payload = {
        "siteUrl": site,
        "urlList": urls
    }

    try:
        response = requests.post(endpoint, params={'apikey': api_key}, json=payload, timeout=15)
        result = response.json()
        if response.status_code == 200:
            print("成功推送到Bing.")
        elif "ErrorCode" in result:
            print("推送到Bing失败，请检查站长平台配置和服务状态。")
    except (requests.RequestException, ValueError):
        print("推送请求失败，请检查网络或服务配置。")


def push_to_baidu(site, urls, token):
    api_url = "https://data.zz.baidu.com/urls"

    payload = "\n".join(urls)
    headers = {"Content-Type": "text/plain"}

    try:
        response = requests.post(api_url, params={'site': site, 'token': token}, data=payload, headers=headers, timeout=15)
        result = response.json()
        if "success" in result and result["success"]:
            print("成功推送到百度.")
        elif "error" in result:
            print("推送到百度失败，请检查站长平台配置和服务状态。")
        else:
            print("百度推送返回了未识别的响应。")
    except (requests.RequestException, ValueError):
        print("推送请求失败，请检查网络或服务配置。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='parse sitemap')
    parser.add_argument('--url', type=str, default=None, help='The url of your website')
    args = parser.parse_args()

    # 获取当前的时间戳作为随机种子
    current_timestamp = int(time.time())
    random.seed(current_timestamp)

    if args.url:
        # 解析urls
        urls = parse_stiemap(args.url)
        if urls is not None:
            # 判断当前urls数量是否超过额度，若超过则取当日最大值，默认为100，可根据实际情况修改
            if len(urls) > QUOTA:
                urls = random.sample(urls, QUOTA)
            # 推送bing
            if os.environ.get('BING_API_KEY'):
                print('正在推送至必应，请稍后……')
                push_to_bing(args.url, urls, os.environ['BING_API_KEY'])
            # 推送百度
            if os.environ.get('BAIDU_TOKEN'):
                print('正在推送至百度，请稍后……')
                push_to_baidu(args.url, urls, os.environ['BAIDU_TOKEN'])
    else:
        print('请前往 Github Action Secrets 配置 URL')
        print('详情参见: https://ghlcode.cn/fe032806-5362-4d82-b746-a0b26ce8b9d9')
