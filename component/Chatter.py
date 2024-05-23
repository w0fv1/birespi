from openai import OpenAI
import asyncio
from openai import AsyncOpenAI

from component.BaseConfig import BaseConfig


class BaseChatter:
    async def answer(self, question: str) -> str:
        raise NotImplementedError


class OpenaiChatterConfig(BaseConfig):
    systemPrompt: str
    apiKey: str
    host: str
    model: str
    temperature: float

    def __init__(
        self,
        systemPrompt: str,
        apiKey: str,
        host: str,
        model: str,
        temperature: float = 1.2,
    ) -> None:
        self.systemPrompt = systemPrompt
        self.type = type
        self.apiKey = apiKey
        self.host = host
        self.model = model
        self.temperature = temperature

    @staticmethod
    def fromDict(json: dict):
        return OpenaiChatterConfig(
            systemPrompt=json["systemPrompt"],
            apiKey=json["apiKey"],
            host=json["host"],
            model=json["model"],
            temperature=json["temperature"],
        )


class OpenaiChatter(BaseChatter):
    config: OpenaiChatterConfig = None
    client: AsyncOpenAI

    cache = {}

    def __init__(self, configDict: dict) -> None:
        self.config = OpenaiChatterConfig.fromDict(configDict)
        self.client = AsyncOpenAI(api_key=self.config.apiKey, base_url=self.config.host)

    async def answer(self, question: str) -> str:

        messages = [
            {"role": "system", "content": self.config.systemPrompt},
            {
                "role": "user",
                "content": question,
            },
        ]

        messageStr = str(messages)

        cache = self.getCache(messageStr)
        if cache is not None:
            return cache

        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.config.model,
            temperature=self.config.temperature,
        )
        result = ""
        for message in chat_completion.choices:
            result += message.message.content

        self.setCache(messageStr, result)

        return result

    def getCache(self, key: str) -> str:
        # 计算key的hash值
        keyHash = hash(key)
        if keyHash not in self.cache:
            return None
        return self.cache.get(keyHash, None)

    def setCache(self, key: str, value: str) -> str:
        keyHash = hash(key)
        self.cache[keyHash] = value


class WebChatter(BaseChatter):
    def answer(self, question: str) -> str:
        return "I don't know"
