import json
import os
import random

import httpx
from loguru import logger

from notify import send

"""
cron: 56 8 * * *
url https://j1.pupuapi.com/client/game/sign/v2/index
Authorization: Bearer xxxxxxxxx
自行添加环境变量 PUPU_AUTH=xxxxxxxxxxxxxxxxx
"""

TITLE = "朴朴超市签到"


class PuPuSuperMarket(object):
    message = dict()

    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF XWEB/6945",
    }

    def __init__(self):
        self.authorization = None

    def sign(self, session: httpx.Client):
        session.headers.update({"Authorization": f"Bearer {self.authorization}"})
        session.headers.update({"Host": "j1.pupuapi.com"})
        session.headers.update({"Origin": "https://ma.pupumall.com"})
        session.headers.update({"Referer": f"https://ma.pupumall.com/"})
        # logger.debug(session.headers)
        res = session.get(
            url="https://j1.pupuapi.com/client/game/sign/v2/index",
            params={
                "lat_y": f"30.648732302456{random.randint(100, 400)}",
                "lng_x": f"104.04953826934{random.randint(100, 400)}",
            },

        )

        logger.debug(res.status_code)
        assert res.status_code == 200

        data = res.json()

        if data.get("errcode") == 0:
            self.message = data.get('data')
        # await sign_in_reward(data.result.signInCount);

        else:
            raise Exception(f"朴朴超市签到失败,{data.get('message')}")

    def get_balance(self, session: httpx.Client):
        res = session.get(
            url="https://j1.pupuapi.com/client/coin",
        )

        logger.debug(res.status_code)
        assert res.status_code == 200

        data = res.json()

        if data.get("errcode") == 0:
            self.message.update({"balance": data.get("data").get("balance")})
        else:
            self.message.update({"balance": None})

    def seed_content(self):
        return f"""
        来源：{TITLE}
        消息：{f"获取 {self.message.get('daily_sign_reward_coin')} 朴朴分"} 
             {self.message.get('reward_explanation')}
             总共有 {self.message.get('balance')} 朴朴分
        """

    def run(self):
        try:

            if not os.getenv("PUPU_AUTH"):
                raise ValueError(f"朴朴超市 环境变量 PUPU_AUTH 不存在")

            self.authorization = os.getenv("PUPU_AUTH")

            with httpx.Client(headers=self.headers, verify=False) as session:

                # 签到
                self.sign(session)
                # 获取 朴朴分
                self.get_balance(session)

        except Exception as e:
            logger.error(e.__str__())
            send("朴朴超市-签到异常", e.__str__())
        else:
            send("朴朴超市-签到成功", self.seed_content())


if __name__ == '__main__':
    pupu = PuPuSuperMarket()
    pupu.run()
