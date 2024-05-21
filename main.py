import signal
import time
import warnings

warnings.filterwarnings("ignore")
from base_component.Logger import BLogger, bLoggerHolder, getLogger
import asyncio
import threading
from Birespi import Birespi, biRespiHolder
from config import BiRespiConfig, birespiConfigHolder, getConfig
from backend.Backend import BirespiBackend, birespiBackendHolder
from util.ConfigUtil import getArgConfigPath, loadJson


version = "0.3.2"


def main():
    birespiConfig: BiRespiConfig = BiRespiConfig(version=version)
    birespiConfigHolder.set(birespiConfig)
    configPath: str = getArgConfigPath()
    getConfig().loadJsonConfig(loadJson(configPath))

    logger: BLogger = BLogger()
    bLoggerHolder.set(logger)

    getLogger().logInfo(f"Starting BiRespi {version}...")

    birespi: Birespi = Birespi()

    biRespiHolder.set(birespi)

    getLogger().logInfo("Birespi loaded.")

    birespiBackend: BirespiBackend = BirespiBackend()

    birespiBackendHolder.set(birespiBackend)

    getLogger().logInfo("Birespi BirespiBackend loaded.")
    birespiBackend.start()
    getLogger().logInfo("Birespi BirespiBackend started.")
    birespi.start()
    getLogger().logInfo("Birespi started.🎉🎉🎉🎉")
    threading.Event().wait()


if __name__ == "__main__":
    main()
