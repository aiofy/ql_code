import httpx
from loguru import logger

from notify import send

refresh_token = "ff7fd57d0ff943b4b43c83b99ed78c6e"

TITLE = "阿里云盘签到"


class AliPan(object):
    authorization = None
    sign_in_count = None
    sign_in_reward_message = None

    headers = {
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Canary": "client=iOS,app=adrive,version=v4.1.3",
        "User-Agent": "AliApp(AYSD/4.1.3) com.alicloud.smartdrive/4.1.3 Version/16.3 Channel/201200 Language/zh-Hans-CN /iOS Mobile/iPhone15,2",
        "Host": "auth.aliyundrive.com",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    }

    def __init__(self, refresh_token: str):
        self.refresh_token = refresh_token

    def verify_token(self, session: httpx.Client):
        res = session.post(
            url="https://auth.aliyundrive.com/v2/account/token",
            json={"grant_type": "refresh_token", "app_id": "pJZInNHN2dZWk8qg", "refresh_token": self.refresh_token}
        )

        logger.debug(res.text)
        data = res.json()

        if data.get("code") == "InvalidParameter.RefreshToken":
            raise Exception("阿里云盘 token 失效")

        self.authorization = f"Bearer {data.get('access_token')}"

    def sign(self, session: httpx.Client):
        session.headers.update({"Authorization": self.authorization})
        session.headers.update({"Host": "member.aliyundrive.com"})
        session.headers.update({"Origin": "https://pages.aliyundrive.com"})
        session.headers.update({"Referer": f"https://pages.aliyundrive.com/"})
        # logger.debug(session.headers)
        res = session.post(
            url="https://member.aliyundrive.com/v1/activity/sign_in_list",
            json={"isReward": False}
        )

        logger.debug(res.status_code)
        logger.debug(res.text)
        data = res.json()

        if data.get("success"):
            self.sign_in_count = data.get('result').get('signInCount')
            logger.success(f"已连续签到 {self.sign_in_count} 天!")
        # await sign_in_reward(data.result.signInCount);

        else:
            raise Exception(f"阿里云盘签到失败,{data.get('message')}")

    def sign_in_reward(self, session: httpx.Client):
        res = session.post(
            url="https://member.aliyundrive.com/v1/activity/sign_in_reward",
            json={"signInDay": self.sign_in_count}
        )

        logger.debug(res.status_code)
        logger.debug(res.text)
        data = res.json()

        if data.get("success"):
            self.sign_in_reward_message = f"奖励: {data.get('result').get('name')} "
            f"{data.get('result').get('description')}"
            f"{data.get('result').get('notice')}"
            logger.success(self.sign_in_reward_message)
        else:
            raise Exception(f"奖励获取失败: {data.get('message')}")

    def seed_content(self):
        return f"""
        
        来源：{TITLE}
        状态：{f"已连续签到 {self.sign_in_count} 天!"} {self.sign_in_reward_message}
        
        """

    def run(self):
        try:
            with httpx.Client(headers=self.headers) as session:
                # 获取 token
                self.verify_token(session)
                # 签到
                self.sign(session)
                # 领取奖励
                self.sign_in_reward(session)
        except Exception as e:
            logger.error(e.__str__())
            send("签到异常", e.__str__())
        else:
            send("签到成功", self.seed_content())


if __name__ == '__main__':
    ali_pan = AliPan(refresh_token)
    ali_pan.run()
