import signal
import time
import warnings

warnings.filterwarnings("ignore")
from base_component.Logger import BLogger, bLoggerHolder, getLogger
import asyncio
import threading
from Birespi import Birespi, biRespiHolder
from config import BiRespiConfig, birespiConfigHolder
from backend.Backend import BirespiBackend, birespiBackendHolder
from util.ConfigUtil import getArgConfigPath, loadJson


version = "0.3.1"


def main():
    logger: BLogger = BLogger()
    bLoggerHolder.set(logger)

    getLogger().log_info(f"Starting BiRespi {version}...")

    configPath: str = getArgConfigPath()

    getLogger().log_info(f"Loading config from {configPath}...")

    birespiConfig: BiRespiConfig = BiRespiConfig(
        jsonConfigPath=configPath, version=version
    )
    birespiConfigHolder.set(birespiConfig)

    getLogger().log_info("Config loaded.")

    birespi: Birespi = Birespi(birespiConfig.birespiConfig)

    biRespiHolder.set(birespi)

    getLogger().log_info("Birespi loaded.")

    birespiBackend: BirespiBackend = BirespiBackend(birespiConfig.getWebUiConfig())

    birespiBackendHolder.set(birespiBackend)

    getLogger().log_info("Birespi BirespiBackend loaded.")
    birespiBackend.start()
    getLogger().log_info("Birespi BirespiBackend started.")
    birespi.start()
    getLogger().log_info("Birespi started.🎉🎉🎉🎉")
    threading.Event().wait()


if __name__ == "__main__":
    main()
