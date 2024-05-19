import warnings

warnings.filterwarnings("ignore")
from base_component.Logger import BLogger, bLoggerHolder,getLogger
import asyncio
import threading
from Birespi import Birespi, biRespiHolder
from config import BiRespiConfig, birespiConfigHolder
from backend.Backend import BirespiBackend, birespiBackendHolder
from util.ConfigUtil import getConfigPath, loadJson


version = "0.2.2"


logger: BLogger = BLogger()

bLoggerHolder.set(logger)

getLogger().log_info(f"Starting BiRespi {version}...")

configPath: str = getConfigPath()

getLogger().log_info(f"Loading config from {configPath}...")

birespiConfig: BiRespiConfig = BiRespiConfig(jsonConfigPath=configPath, version=version)

birespiConfigHolder.set(birespiConfig)

getLogger().log_info("Config loaded.")

birespi: Birespi = Birespi(birespiConfig.birespiConfig)

biRespiHolder.set(birespi)

getLogger().log_info("Birespi loaded.")

birespiUi: BirespiBackend = BirespiBackend(birespiConfig.getWebUiConfig())

birespiBackendHolder.set(birespiUi)

getLogger().log_info("Birespi BirespiBackend loaded.")
birespiUi.start()
getLogger().log_info("Birespi BirespiBackend started.")
birespi.startRespi()
getLogger().log_info("Birespi started.")
