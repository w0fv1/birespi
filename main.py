import asyncio
import threading
from Birespi import Birespi
from config import BiRespiConfig
from ui.Ui import BirespiUi
from util.ConfigUtil import getConfigPath, loadJson
from system import Context

configPath: str = getConfigPath()

birespiConfig: BiRespiConfig = BiRespiConfig(jsonConfigPath=configPath)
Context.getBirespiConfig = lambda: birespiConfig

print(birespiConfig)

birespi: Birespi = Birespi(birespiConfig.birespiConfig)
Context.getBirespi = lambda: birespi

birespiUi: BirespiUi = BirespiUi(birespiConfig.getWebUiConfig())
Context.getBirespiUi = lambda: birespiUi

if __name__ == "__main__":

    birespiUi.start()
    birespi.startRespi()
