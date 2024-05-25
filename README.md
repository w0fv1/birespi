# Birespi 哔哩哔哩应答姬 V0.6.1 [建设中...]

哔哩哔哩应答姬是一个基于AI的自动语音回复直播间弹幕的Bot.

部署在电脑上之后, 会自动监听指定的直播间弹幕, 并且自动语音回复弹幕.

# 计划

1. 1.0目标成为一个好用实用的无人直播间互动应答姬Bot, 无人直播姬, 面向普通用户, 目标是提高易用性, 降低门槛, 提供更多的功能
2. 2.0将硬分叉出一个直播间互动开发框架, 1.0的应答姬bot将继续维护. 另一个分支将框架化, 面向开发者, 提供更多的开发api.

# 受众

社恐主播和无人直播

# 特性

- 自动语音回复弹幕
- 可以支持多种LLM，TTS，各个平台弹幕接入
- RAG资料库
- 良好的后台管理界面
- 支持多种直播平台

# 如何使用

### 0. 运行环境

需要安装`Python 3.12`环境, 请自行安装

可以尝试使用其他版本Python, 但是未经测试, 请自行测试

项目依赖ffmpeg, 在lib已经包含了`ffmpeg,ffplay,ffprobe`,
并且已经配置好了config,指向了lib中的`ffmpeg,ffplay,ffprobe,` 如果需要自定义,
请修改`config.py`,或者通过指定的config.json文件配置.

### 1. 创建虚拟环境, 安装依赖

#### 脚本安装:

运行脚本`install.sh`或`install.ps1`或者手动安装.

#### 手动安装:

linux, 手动安装:

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

windows, powershell, 手动安装:

```shell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

windows, cmd, 手动安装:

```shell
python -m venv venv
.\venv\Scripts\Activate.bat
pip install -r requirements.txt
```

### 2. 修改配置

应答姬需要配置文件`config.json`, 请复制`config.example.json`为`config.json`

linux,复制:

```shell
cp config.example.py config.py
```

windows, powershell, 复制:

```shell
Copy-Item config.example.py config.py
```

windows, cmd, 复制:

```shell
copy config.example.py config.py
```

请修改`config.example.json`, 不然应答姬无法正常运行!

config的格式为json:

```json
{
  "chatter": { //这里是配置chatter组件的参数
    "type": "OpenaiChatter", // 这里是chatter的类型, 目前就一个OpenaiChatter
    "OpenaiChatter": { //这里是OpenaiChatter的配置
      "systemPrompt": "", //这里是系统提示, 根据需要填写
      "apiKey": "需要填写apiKey", //这里是OpenAI对话协议的API Key
      "host": "https://api.openai.com", //这里是OpenAI对话协议的的API Host
      "model": "gpt-3.5-turbo", //这里是OpenAI对话协议的的模型
      "temperature": 1.2 //这里是OpenAI对话协议的的温度
    }
  },
  "live_event_receiver": { //这里是配置直播事件接收器的参数
    "type": "BiliOpenLiveEventReceiver", //这里是直播事件接收器的类型, 目前有两个BiliOpenLiveEventReceiver, 这个是官方的B站直播事件接收器, ThirdLiveEventReceiver, 这个是第三方的直播事件接收器
    "BiliOpenLiveEventReceiver": { //这里是BiliOpenLiveEventReceiver的配置
      "idCode": "需要填写idCode", //这里是B站直播间的身份码在https://play-live.bilibili.com/的右下角去看
      "appId": 0, //这里是B站直播间appId, 去B站开放平台互动直播申请
      "key": "需要填写key", //这里是B站开放平台互动直播的key
      "secret": "需要填写secret", //这里是B站开放平台互动直播的secret
      "host": "https://live-open.biliapi.com" //这里是B站开放平台互动直播的host,一般不需要修改
    },
    "ThirdLiveEventReceiver": {
      "username": "需要填写username", //这里是需要填写username, 电话或者邮箱
      "password": "需要填写password", //这里是需要填写你的密码
      "roomId": 0, //这里是需要填写你的直播间ID,在直播间的url中可以找到
      "buvid3": "需要去浏览器寻找cookie中的buvid3然后填写" //这里是需要填写你的buvid3, 在浏览器的cookie中可以找到. 在浏览器中按F12, 然后找到应用程序, cookie, 找到https://www.bilibili.com 找到buvid3, 然后复制过来
    }
  }
}
```

其中一定需要修改的值有chatter.OpenaiChatter的apiKey,host和live_event_receiver.BiliOpenLiveEventReceiver的idCode,appId,key,secret或者live_event_receiver.ThirdLiveEventReceiver的username,password,roomId,buvid3,找到你使用的直播平台的配置,然后填写.

其他配置通常情况下不需要修改, 如果有需要, 请看`system/config.py`文件, 里面有所有的配置项.

### 3. 运行

#### 脚本运行:

运行会自动读取`config.json`文件, 如果需要自定义配置文件位置,
请使用`config`参数例如`python main.py config=/path/to/config.json`

项目根目录有`run.sh`和`run.ps1`脚本, 可以直接运行, 如果需要自定义配置文件位置,
请修改脚本

#### 手动运行:

shell,运行:

```shell
.\venv\Scripts\Activate.ps1
python main.py
```

如果`config.json`的位置需要自定义, 请使用:

```shell
python main.py config=/path/to/config.json
```

windows, powershell, 运行:

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

如果`config.json`的位置需要自定义, 请使用:

```powershell
python main.py config=/path/to/config.json
```

windows, cmd, 运行:

```shell
.\venv\Scripts\Activate.bat
python main.py
```

如果`config.json`的位置需要自定义, 请使用:

```shell
python main.py config=/path/to/config.json
```

### 4. 运行成功

可访问`http://localhost:8000`进入后台

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

本项目测试不完全, 如果有任何问题, 请提issue, 谢谢!

作者放弃一切权利, 任何人可以自由使用, 修改, 分发, 但是请保留原作者信息, 谢谢!