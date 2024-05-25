import signal
import time
import warnings

warnings.filterwarnings("ignore")
from system.Logger import BLogger, bLoggerHolder, getLogger
import asyncio
import threading
from system.Birespi import Birespi, biRespiHolder
from system.Config import BiRespiConfig, birespiConfigHolder, getConfig
from system.backend.Backend import BirespiBackend, birespiBackendHolder
from util.ConfigUtil import getArgConfigPath, loadJson


version = "0.6.1"


def main():
    birespiConfig: BiRespiConfig = BiRespiConfig(
        jsonConfigPath=getArgConfigPath(), version=version
    )
    birespiConfigHolder.set(birespiConfig)
    print(getConfig().getJsonConfig())
    getConfig().saveJsonConfig()
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
