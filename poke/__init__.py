from pathlib import Path
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import PokeNotifyEvent
import random
import asyncio
from typing import Dict
try:
    import ujson as json
except ModuleNotFoundError:
    import json


#戳一戳插件，戳一戳可以发送随机星白语录


disable_group = [] #填写不启用的群，int型
text_path = Path(__file__).parent / "xb_text.json"
last_invoke_time: Dict[str, float] = {}

poke_ = on_notice(priority=7, block=False)
@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    #是否符合触发事件的条件
    if event.self_id != event.target_id and event.group_id in disable_group:
        return
    #cd控制，避免刷屏
    event_key = f"{event.group_id}"
    current_time = asyncio.get_event_loop().time()
    if last_invoke_time.get(event_key, 0) + 3 > current_time:
        return  
    last_invoke_time[event_key] = current_time
    #功能
    xbyl_list = json.load(open(text_path, "r", encoding="utf-8-sig"))
    random_num = str(random.randint(2, 14965))
    text = xbyl_list[random_num]
    await poke_.finish(text)


