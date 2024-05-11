# Birespi 哔哩哔哩应答姬 V0.1.0

哔哩哔哩应答姬是一个基于AI的自动语音回复直播间弹幕的Bot.

部署在电脑上之后, 会自动监听指定的直播间弹幕, 并且自动语音回复弹幕.

# 受众

社恐主播和无人直播

目前未提供易用UI, 需要一定的编程基础, 未来会提供更好的UI

# 特性

- 自动语音回复弹幕
- 可以支持多种LLM，TTS，各个平台弹幕接入

# 如何使用

1. 创建虚拟环境, 安装依赖

```shell
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

2. 编写配置

应答姬需要配置文件`config.json`, 请复制`config.example.json`为`config.json`

```shell
cp config.example.py config.py
```

请修改`config.example.json`, 不然应答姬无法正常运行!

其中一定需要修改的值有chatter.OpenaiChatter的apiKey,host和danmu_receiver.BiliOpenDanmuReceiver的idCode,appId,key,secret：

| 必填配置项                                  | 说明                        |
| ------------------------------------------- | --------------------------- |
| chatter.OpenaiChatter.apiKey                | OpenAI协议的API Key         |
| chatter.OpenaiChatter.host                  | OpenAI协议的API Host        |
| danmu_receiver.BiliOpenDanmuReceiver.idCode | B站直播间ID                 |
| danmu_receiver.BiliOpenDanmuReceiver.appId  | B站直播间appId              |
| danmu_receiver.BiliOpenDanmuReceiver.key    | B站开放平台互动直播的key    |
| danmu_receiver.BiliOpenDanmuReceiver.secret | B站开放平台互动直播的secret |


其他配置通常情况下不需要修改, 如果有需要, 请看config.py

3. 运行

默认读取项目根目录下的`config.json`文件, 直接运行:

```shell
python main.py
```

如果`config.json`的位置需要自定义, 请使用:

```shell
python main.py config=/path/to/config.json
```

# TODO

1. 增加gpt-sovits的部署和支持
2. 增加第三方的弹幕接入
3. 增加管理界面
    1. 查看弹幕
    2. 查看回复
    3. 查看状态
    4. 修改配置
    5. 查看日志
4. 更好的打包, 例如exe, docker等
5. 更好的文档

# 最后

如果有任何问题, 请提issue, 谢谢!

