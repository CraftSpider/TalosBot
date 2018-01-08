"""
    The start of an attempt to rewrite Chatzy Talos using a python async framework
    This will go wonderfully

    author: CraftSpider
"""

import asyncio
import aiohttp


async def run():
    print("Running Talos")
    session = aiohttp.ClientSession()
    try:
        login_data = {
            "X7245": "undefined",
            "X5141": "",
            "X5865": "",
            "X2940": "sign.htm",
            "X7960": 1508500329,
            "X5481": 1,
            "X3190": "sign",
            "X6511": "talos.ptp@gmail.com",
            "X3361": 1,
            "X8182": "",
            "X9170": "***REMOVED***",
            "X3941": "",
            "X8170": "",
            "X3145": "http://www.chatzy.com/",
            "X6746": 1
        }
        async with session.post("https://www.chatzy.com/", data=login_data) as response:
            print(await response.text())
        # async with session.get("https://www.chatzy.com/#ok:entered:Chatzy") as response:
        #     print(await response.text())
        join_room_data = {
            "jsonp:X7245": None,
            "X5141": "x3VG91jWcdMVECzEty4tpA - talos.ptp%40gmail.com%26izln3rlnfc7c%261%3aTalos%261461266736%261461525936%26%261%262",
            "X5865": 65837708618840,
            "X2940": 65837708618840,
            "X8385": "http://www.chatzy.com/",
            "X7960": 1508500329,
            "X5481": 1,
            "X3190": "enter",
            "X6432": "Talos[Bot]",
            "X8049": "FF0000",
            "X6671": "FF0000",
            "X6577": "",
            "X5455": 2,
            "X7245": "X6766",
            "X2457": 21,
            "X7380": "",
            "X7469": 1515441130093
        }
        async with session.put("http://us21.chatzy.com/", data=join_room_data) as response:
            print(await response.text())
    except Exception as e:
        print(e)
    finally:
        session.close()


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.run_forever()


main()
