"""
    The start of an attempt to rewrite Chatzy Talos using a python async framework
    This will go wonderfully

    author: CraftSpider
"""

import asyncio
import aiohttp
from yarl import URL


async def run():
    print("Running Talos")
    session = aiohttp.ClientSession()
    try:
        login_data = {  # TODO: Figure out which of these can be removed?
            # "X7245": "undefined",  # Unknown purpose
            # "X5141": "",  # Appears to hold the user string
            # "X5865": "",  # always defined
            # "X2940": "sign.htm",  # always defined
            "X7960": 1508500329,
            "X5481": 1,
            "X3190": "sign",
            "X6511": "talos.ptp@gmail.com",  # login email
            "X3361": 1,  # We're registered. 2 if we were registering.
            # "X8182": "",  # One time code for lost password
            "X9170": "***REMOVED***",  # login password
            # "X3941": "",  # New Password field
            # "X8170": "",  # Confirm new password field
            # "X3145": "http://www.chatzy.com/",  # Not sure what this is for
            # "X7719": 1  # Passed if we want to log out others
            # "X8382": 1  # Passed if we want to stay logged in
            # "X6746": 1  # Unknown purpose
        }
        async with session.post("https://www.chatzy.com/", data=login_data) as response:
            # print(await response.text())
            usercookie = response.cookies["ChatzyUser"]
            usercookie["expires"] = ""
            session.cookie_jar.update_cookies(response.cookies)
        for cookie in session.cookie_jar:
            print(cookie)
        print()
        # async with session.get("https://www.chatzy.com/#ok:entered:Chatzy") as response:
        #     print(await response.text())
        # join_room_data = {
        #     "jsonp:X7245": None,
        #     "X5141": "x3VG91jWcdMVECzEty4tpA - talos.ptp%40gmail.com%26izln3rlnfc7c%261%3aTalos%261461266736%261461525936%26%261%262",
        #     "X5865": 65837708618840,
        #     "X2940": 65837708618840,
        #     "X8385": "http://www.chatzy.com/",
        #     "X7960": 1508500329,
        #     "X5481": 1,
        #     "X3190": "enter",
        #     "X6432": "Talos[Bot]",
        #     "X8049": "FF0000",
        #     "X6671": "FF0000",
        #     "X6577": "",
        #     "X5455": 2,
        #     "X7245": "X6766",
        #     "X2457": 21,
        #     "X7380": "",
        #     "X7469": 1515441130093
        # }
        session.cookie_jar.update_cookies({"ChatzyPrefs2": "Talos[Bot]&FF0000"}, URL("http://chatzy.com"))
        join_room_data = {
            "X7960": 1508500329,
            "X5481": 1,
            # This is the important one. Contains user data. Figure out how to generate it.
            "X1263": "I4SiNhTbCS5PFVAPR+iZqw-65837708618840%2665837708618840%26https%3a%2f%2fwww.chatzy.com%2f%26X7060%261515655529%26KHAWBRVB%26Talos%5bBot%5d%26FF0000%26%26US%3aUnited+States%3a%26talos.ptp%40gmail.com%26izln3rlnfc7c%261%3aTalos%261461266736%261461525936%26%261%262",
            "X2798": ""
        }
        async with session.put("http://us21.chatzy.com/65837708618840", data=join_room_data) as response:
            pass
            print(response.cookies)
        post_message_data = {
            "X7960": 1508500329,
            "X7245": "X2928",
            "X1263": "O3RQYwKeg7BMOoIQX6gn7A-65837708618840%2665837708618840%26https%3a%2f%2fwww.chatzy.com%2f%26X6046%261515655716%26KHAWBRVB%26Talos%5bBot%5d%26FF0000%26%26US%3aUnited+States%3a%26talos.ptp%40gmail.com%26izln3rlnfc7c%261%3aTalos%261461266736%261461525936%26%261%262",
            "X7162": 150000,
            "X9102": 1515655716,
            "X7974": "Test Message",
            "X6746": 1
        }
        async with session.put("http://us21.chatzy.com/65837708618840", data=post_message_data) as response:
            print(await response.text())
    finally:
        session.close()


def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(run())
    loop.run_until_complete(task)


main()
