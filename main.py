import asyncio
import threading
from Birespi import Birespi
from config import BiRespiConfig
from ui.UI import BirespiUI
from util.ConfigUtil import getConfigPath, loadJson
from system import Context

configPath: str = getConfigPath()
birespiConfig: BiRespiConfig = BiRespiConfig(jsonConfigPath=loadJson(configPath))
print("configPath:", configPath)

birespi: Birespi = Birespi(birespiConfig.birespiConfig)
Context.getBirespi = lambda: birespi

if __name__ == "__main__":
    uiThread = threading.Thread(target=BirespiUI(birespiConfig.getWebUiConfig()).start)
    uiThread.start()
    birespi.startRespi()
