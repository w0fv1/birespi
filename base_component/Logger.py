import inspect
import logging
import datetime
import os


class BLogger:
    log: logging.Logger = None

    def __init__(self):
        self.log = logging.getLogger("BLogger")
        self.log.setLevel(logging.DEBUG)

        # Create file handler which logs even debug messages
        filename = f'log/birespi-log-{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'
        if not os.path.exists("log"):
            os.makedirs("log")

        file_handler = logging.FileHandler(filename, mode="a")
        file_handler.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        class CustomFormatter(logging.Formatter):
            def format(self, record):
                # 获取调用栈
                stack = inspect.stack()
                # 获取上一层的函数名
                # 假设我们想要的是调用当前函数的函数名，所以是第3层
                # 如果你的代码结构不同，你可能需要调整这个索引
                func_name = stack[2][3]
                # 设置funcName属性
                record.funcName = func_name
                # 使用父类的format方法来格式化记录
                return super().format(record)

        # Create formatter and add it to the handlers
        formatter = CustomFormatter(
            "[%(asctime)s]-[%(name)s-%(levelname)s]-%(funcName)s(): %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.log.addHandler(file_handler)
        self.log.addHandler(console_handler)

    def log_message(self, message: str):
        self.log.info(message)

    def log_info(self, message):
        self.log.info(message)

    def log_error(self, message):
        self.log.error(message)

    def log_warning(self, message):
        self.log.warning(message)

    def log_debug(self, message):
        self.log.debug(message)

    def log_critical(self, message):
        self.log.critical(message)



class BLoggerHolder:
    logger: BLogger = None

    def set(self, logger: BLogger):
        self.logger = logger

    def get(self) -> BLogger:
        return self.logger
    
bLoggerHolder: BLoggerHolder = BLoggerHolder()