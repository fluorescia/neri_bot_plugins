from nonebot.adapters.onebot.v11 import Bot, Message ,GroupMessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.params import CommandArg
from nonebot import on_command
from nonebot.rule import Rule
from pathlib import Path
import random
import os
try:
    import ujson as json
except ModuleNotFoundError:
    import json
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from typing import Dict

#随机语音
"""
发送星白随机语音
指令：

随机语音？[狩叶/春香|诺瓦|真白|音理|房东|鹰世|野鸟/珍妮弗|花江]
ps.如果不指定人物，则从狩叶、诺瓦、真白、音理中任选一条。

语音文本 --显示上一条发送语音的文本内容

示例：
随机语音
随机语音狩叶
随机语音诺瓦
语音文本
"""


enable_group = [] #填写需要启用功能的群，int型

async def checker_group(event: GroupMessageEvent) -> bool:
    return True if event.group_id in enable_group else False


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


raillvoice = on_command("随机语音", permission=GROUP, priority=5, block=True, rule=Rule(checker_group))
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

votext = on_command("语音文本", permission=GROUP, priority=5, block=True, rule=Rule(checker_group))
@votext.handle()
async def _(event: GroupMessageEvent):
    text = text_of_pre.get(str(event.group_id), '')
    if text:
        await votext.finish(text)


raillvoice2 = on_command("星白语音", permission=GROUP, priority=5, block=True, rule=Rule(checker_group))
@raillvoice2.handle()
async def _(arg: Message = CommandArg()):
    msg = arg.extract_plain_text().strip()
    voice_path = voicefile_path / f"{msg}.mp3"

    if voice_path.is_file():
        result = MessageSegment.record(voice_path)
        await raillvoice2.send(result)
    else:
        await raillvoice2.send("无该语音文件")

