import warnings

warnings.filterwarnings("ignore")
from base_component.Logger import BLogger, bLoggerHolder
import asyncio
import threading
from Birespi import Birespi, biRespiHolder
from config import BiRespiConfig, birespiConfigHolder
from backend.Backend import BirespiBackend, birespiBackendHolder
from util.ConfigUtil import getConfigPath, loadJson


version = "0.2.2"


logger: BLogger = BLogger()

bLoggerHolder.set(logger)

bLoggerHolder.get().log_message(f"Starting BiRespi {version}...")

configPath: str = getConfigPath()

bLoggerHolder.get().log_info(f"Loading config from {configPath}...")

birespiConfig: BiRespiConfig = BiRespiConfig(jsonConfigPath=configPath, version=version)

birespiConfigHolder.set(birespiConfig)

bLoggerHolder.get().log_info("Config loaded.")

birespi: Birespi = Birespi(birespiConfig.birespiConfig)

biRespiHolder.set(birespi)

bLoggerHolder.get().log_info("Birespi loaded.")

birespiUi: BirespiBackend = BirespiBackend(birespiConfig.getWebUiConfig())

birespiBackendHolder.set(birespiUi)

bLoggerHolder.get().log_info("Birespi BirespiBackend loaded.")
birespiUi.start()
bLoggerHolder.get().log_info("Birespi BirespiBackend started.")
birespi.startRespi()
bLoggerHolder.get().log_info("Birespi started.")
