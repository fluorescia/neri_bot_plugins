from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from pathlib import Path
import random
from nonebot.rule import Rule
try:
    import ujson as json
except ModuleNotFoundError:
    import json

#群友每次说话有概率触发发送一条语录，语录发送会按游戏内文本顺序进行

#语录文件
text_path = Path(__file__).parent / "xb_text.json"
xbyl = json.load(open(text_path, "r", encoding="utf-8-sig"))

#计数相关
count_path = Path(__file__).parent / "xb_count.json"
count_list = json.loads(count_path.read_text("utf-8")) if count_path.is_file() else {}

#填写需要启用的群，int型
enable_group = []


async def select_msg(group: int):
    pre_num = count_list.get(str(group), 2)
    post = xbyl[str(pre_num)]
    next_post_num = pre_num + 1
    if len(post) < 17:
        post = f"{post} {xbyl[str(next_post_num)]}"
        next_post_num += 1
        if len(post) < 20:
            post = f"{post} {xbyl[str(next_post_num)]}"
            next_post_num += 1
    
    if next_post_num > 14965: #到了结尾，重新开始
        next_post_num = 2
    
    #记录计数
    count_list[f"{group}"] = next_post_num
    count_path.write_text(json.dumps(count_list, indent = 4, ensure_ascii = False),  encoding="utf-8")
    
    return post


async def checker_group(event: GroupMessageEvent) -> bool:
    return True if event.group_id in enable_group else False

poke2 = on_message(priority = 7, block = False ,rule = Rule(checker_group))
@poke2.handle()
async def _(event: GroupMessageEvent):
    if 0.05 > random.random():
        await poke2.finish(await select_msg(group = event.group_id))