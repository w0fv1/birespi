import asyncio
import threading
from Birespi import Birespi
from config import BiRespiConfig
from ui.ui import BirespiUI
from util.ConfigUtil import argDict, getConfigPath, loadJson
import uvicorn

configPath = getConfigPath()

print("configPath:", configPath)

birespi: Birespi = Birespi(
    BiRespiConfig(jsonConfigPath=loadJson(configPath)).birespiConfig
)


async def startBirespi(birespi: Birespi):
    await birespi.startRespi()

    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    threading.Thread(target=BirespiUI(birespi).startUi).start()
    asyncio.run(startBirespi(birespi))
