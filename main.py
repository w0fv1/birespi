import asyncio
from Birespi import Birespi
from config import BiRespiConfig
from util.ConfigUtil import argDict, getConfigPath, loadJson

configPath = getConfigPath()

print("configPath:", configPath)

async def startBirespi():
    await Birespi(
        BiRespiConfig(jsonConfigPath=loadJson(configPath)).birespiConfig
    ).startRespi()

    # 这里假设 main 中有持续运行的任务
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(startBirespi())
