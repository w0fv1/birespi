import inspect
import logging
import datetime
import os
from system.Config import getConfig


class BLogger:
    log: logging.Logger = None

    def __init__(self):
        self.log = logging.getLogger("BLogger")
        self.log.setLevel(
            logging.getLevelName(getConfig().getLoggerConfigDict()["log_level"].upper())
        )

        # Create file handler which logs even debug messages
        filename: str = getConfig().getLoggerConfigDict()["filename"]
        filename = filename.replace(
            "%(today)s", datetime.datetime.now().strftime("%Y-%m-%d")
        )
        if not os.path.exists("log"):
            os.makedirs("log")

        fileHandler = logging.FileHandler(filename, mode="a")
        fileHandler.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                # 获取调用栈
                stack = inspect.stack()
                # 获取上一层的函数名
                # 假设我们想要的是调用当前函数的函数名，所以是第3层
                # 如果你的代码结构不同，你可能需要调整这个索引
                funcName = stack[2][3]
                # 设置funcName属性
                record.funcName = funcName
                # 使用父类的format方法来格式化记录
                return super().format(record)

        # Create formatter and add it to the handlers
        formatter = CustomFormatter(getConfig().getLoggerConfigDict()["formatter"])
        fileHandler.setFormatter(formatter)
        consoleHandler.setFormatter(formatter)

        # Add the handlers to the logger
        self.log.addHandler(fileHandler)
        self.log.addHandler(consoleHandler)

    def loj(self, message: str):
        self.log.info(message)

    def logInfo(self, message):
        self.log.info(message)

    def logError(self, message):
        self.log.error(message)

    def logWarning(self, message):
        self.log.warning(message)

    def logDebug(self, message):
        self.log.debug(message)

    def logCritical(self, message):
        self.log.critical(message)

    def getLogFiles(self) -> list[str]:
        return os.listdir("log")

    def getLog(self, filename: str) -> str:
        with open(f"log/{filename}", "r") as f:
            return f.read()


class BLoggerHolder:
    logger: BLogger = None

    def set(self, logger: BLogger):
        self.logger = logger

    def get(self) -> BLogger:
        return self.logger


bLoggerHolder: BLoggerHolder = BLoggerHolder()


def getLogger() -> BLogger:
    return bLoggerHolder.get()
