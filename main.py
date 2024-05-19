import asyncio
import threading
from Birespi import Birespi
from base_component.Logger import BLogger
from config import BiRespiConfig
from backend.Backend import BirespiBackend
from util.ConfigUtil import getConfigPath, loadJson
from system import Context

version = "0.2.2"


logger: BLogger = BLogger()
Context.getLogger = lambda: logger

logger.log_message(f"Starting BiRespi{version}...")

configPath: str = getConfigPath()

birespiConfig: BiRespiConfig = BiRespiConfig(jsonConfigPath=configPath, version=version)
Context.getBirespiConfig = lambda: birespiConfig

print(birespiConfig)

birespi: Birespi = Birespi(birespiConfig.birespiConfig)
Context.getBirespi = lambda: birespi

birespiUi: BirespiBackend = BirespiBackend(birespiConfig.getWebUiConfig())
Context.getBirespiUi = lambda: birespiUi

if __name__ == "__main__":

    birespiUi.start()
    birespi.startRespi()
