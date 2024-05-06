
from nonebot import on_notice, on_message, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import PokeNotifyEvent, Message ,GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.rule import Rule

from pathlib import Path
import asyncio
import random
from typing import Dict
try:
    import ujson as json
except ModuleNotFoundError:
    import json

__plugin_usage__ = """
usage：
    一共3个插件的整合：
    1. 戳一戳随机掉落星白语录
    2. 发送星白随机语音
        指令：
        * 随机语音?[狩叶/春香|诺瓦|真白|音理|房东|鹰世|野鸟/珍妮弗|花江]
            ps.如果不指定人物，则从狩叶、诺瓦、真白、音理中任选一条。
        * 语音文本 --显示上一条发送语音的文本内容
        * 星白语音[编号]
        示例：
            随机语音
            随机语音狩叶
            随机语音诺瓦
            语音文本
            星白语音kar0619
    3. 群消息有概率触发顺序发送语录
""".strip()

###戳一戳插件，戳一戳可以发送随机星白语录
disable_group = [] #填写不启用的群，int型

text_path = Path(__file__).parent / "xb_text.json"
last_invoke_time: Dict[str, float] = {}

poke_ = on_notice(priority=7, block=False)
@poke_.handle()
async def _poke_event(event: PokeNotifyEvent):
    #是否符合触发事件的条件
    if event.group_id in disable_group:
        return
    if event.self_id != event.target_id:
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









###随机语音
enable_group_voice = [] #填写需要启用功能的群，int型

async def checker_group_voice(event: GroupMessageEvent) -> bool:
    return True if event.group_id in enable_group_voice else False


#所有语音的文本信息列表
all_voice_info_path = Path(__file__).parent / "voice_info.json"
all_voice_info_list = json.loads(all_voice_info_path.read_text("utf-8"))

#语音文件路径
voicefile_path = Path(__file__).parent / "voice_files"

#长语音（大于4秒）文件名列表
long_voice_path = Path(__file__).parent / "long_voice_dict.json"
long_voice_list = json.loads(long_voice_path.read_text("utf-8"))

#保存上一个语音的文本
text_of_pre: Dict[str, str] = {}


raillvoice = on_command("随机语音", permission=GROUP, priority=5, block=True, rule=Rule(checker_group_voice))
@raillvoice.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    key = ''

    #将指令的参数转化成符号
    if msg:
        namedict = {
            '音理':'ner',
            '诺瓦':'noi',
            '真白':'mas',
            '狩叶':'kar',
            '春香':'kar',
            '野鸟':'jib',
            '珍妮弗':'jib',
            '鹰世':'tak',
            '花江':'han',
            '房东':'ooy',
        }
        key = namedict.get(msg, '')
    
    #根据有无参数来筛选符合条件的所有语音文件
    eligible_voice_list = []
    if key:
        for i in long_voice_list:
            if i[0:3] == key:
                eligible_voice_list.append(i)      
    else:
        #如果未指定是谁，则在三小只的语音里选择
        for i in long_voice_list:
            if i[0:3] in ['ner','noi','mas','kar']:
                eligible_voice_list.append(i)  
    
    #随机选择其中一个语音文件
    voice = random.choice(eligible_voice_list)

    #保存语音的文本，供“语音文本”功能使用
    try:
        text_of_voice = f"{all_voice_info_list[voice][1]}\n({voice[:-4]})"
    except KeyError:
        text_of_voice = '未能查询到文本'
    text_of_pre[str(event.group_id)] = text_of_voice

    #获取目的语音文件，发送语音
    result = MessageSegment.record(voicefile_path / voice)
    await raillvoice.send(result)

votext = on_command("语音文本", permission=GROUP, priority=5, block=True, rule=Rule(checker_group_voice))
@votext.handle()
async def _(event: GroupMessageEvent):
    text = text_of_pre.get(str(event.group_id), '')
    if text:
        await votext.finish(text)


raillvoice2 = on_command("星白语音", permission=GROUP, priority=5, block=True, rule=Rule(checker_group_voice))
@raillvoice2.handle()
async def _(arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    voice_path = voicefile_path / f"{msg}.mp3"

    if voice_path.is_file():
        result = MessageSegment.record(voice_path)
        await raillvoice2.send(result)
    else:
        await raillvoice2.send("无该语音文件")








###随机文本
#语录文件
text_path = Path(__file__).parent / "xb_text.json"
xbyl = json.load(open(text_path, "r", encoding="utf-8-sig"))

#计数相关
count_path = Path(__file__).parent / "xb_count.json"
count_list = json.loads(count_path.read_text("utf-8")) if count_path.is_file() else {}

#填写需要启用的群，int型
enable_group_text = []

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


async def checker_group_text(event: GroupMessageEvent) -> bool:
    return True if event.group_id in enable_group_text else False

poke2 = on_message(priority = 7, block = False ,rule = Rule(checker_group_text))
@poke2.handle()
async def _(event: GroupMessageEvent):
    if random.randint(1, 30) == 1: #设置触发频率
        await poke2.finish(await select_msg(group = event.group_id))      
