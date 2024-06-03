"""
cron: 56 9 * * *
自行添加环境变量 QL_BDUSS_BFESS=xxxxxx,xxxxxxx
多账号 , 分隔
"""
import json
import os

import httpx
from loguru import logger

from notify import send


TITLE = "度加创作工具签到"


class DuJia(object):
    balance = 0

    def sign(self, session: httpx.Client, token: str):

        url = "https://aigc.baidu.com/aigc/saas/pc/v1/member/task/finish"

        data = {
            "scene": "sign_in"
        }

        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            'Cache-Control': "no-cache",
            'Content-Type': "application/json",
            'Origin': "",
            'https': "//aigc.baidu.com",
            'Pragma': "no-cache",
            'Referer': "",
            'Sec-Ch-Ua': "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            'Sec-Ch-Ua-Mobile': "?0",
            'Sec-Ch-Ua-Platform': "\"Windows\"",
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-origin",
            'Cookie': f"BDUSS_BFESS={token}"
        }

        res = session.post(url=url, headers=headers, json=data)

        logger.debug(res.text)
        jdata = res.json()

        if jdata["errmsg"] == "Success":
            logger.success(f"{jdata['data']['reward']}")
        else:
            raise Exception(f"{TITLE} {jdata['errmsg']}")

    def points_balance(self, session: httpx.Client, token: str):
        url = "https://aigc.baidu.com/aigc/saas/pc/v1/payment/pointsBalance"

        headers = {
            'Accept': "*/*",
            'Accept-Encoding': "gzip, deflate, br, zstd",
            'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "aigc.baidu.com",
            'Pragma': "no-cache",
            'Referer': "https://aigc.baidu.com/make?tab=create",
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-origin",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            'sec-ch-ua': "\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            'sec-ch-ua-mobile': "?0",
            'sec-ch-ua-platform': "\"Windows\"",
            'Cookie': f"BDUSS_BFESS={token}"
        }

        res = session.get(url, headers=headers)
        logger.debug(res.text)
        jdata = res.json()

        if jdata["errmsg"] == "Success":
            logger.success(f"{jdata['data']['balance']}")
            self.balance = jdata["data"]["balance"]
        else:
            raise Exception(f"{TITLE} {jdata['errmsg']}")

    def seed_content(self):
        return f"""

        来源：{TITLE}
        状态：完成签到打卡任务 余额 {self.balance}

        """

    def run(self):
        try:

            token = os.getenv("QL_BDUSS_BFESS")
            if not token:
                raise ValueError(f"{TITLE}-环境变量 QL_BDUSS_BFESS 不存在")

            for token in token.split(","):
                with httpx.Client() as session:
                    # 签到
                    self.sign(session, token)
                    # 获取余额
                    self.points_balance(session, token)

        except Exception as e:
            logger.error(e.__str__())
            send(f"{TITLE}-签到异常", e.__str__())
        else:
            send(f"{TITLE}-签到成功", self.seed_content())


if __name__ == '__main__':
    dj = DuJia()
    dj.run()
