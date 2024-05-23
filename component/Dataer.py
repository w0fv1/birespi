import os


class BaseDataer:

    def __init__(self) -> None:
        pass

    def loadData(self, dataPath: str):
        pass

    async def getSimilarity(self, fromData: str):
        pass


class DataerConfig:
    dataPath: str = None

    def __init__(self, dataPath: str) -> None:
        self.dataPath = dataPath

    @staticmethod
    def fromDict(dict: dict) -> "DataerConfig":
        return DataerConfig(dict["dataPath"])


class ADataer(BaseDataer):
    data: dict[str, str] = {}
    config: DataerConfig = None

    def __init__(self, config: dict) -> None:
        print(config, type(config), config)
        self.config = DataerConfig.fromDict(config)
        self.loadData(self.config.dataPath)

    def loadData(self, dataPath: str):
        self.data = {}
        # 读取dataPath文件夹下所有文件的内容，存入self.data

        for file in os.listdir(dataPath):
            print(type(file), file)
            with open(f"{dataPath}/{file}", "r") as f:
                filename: str = file.replace(".", "")
                content: str = f.read()
                self.data[filename] = content

    def watchFile(self, filename: str):
        pass

    async def getSimilarity(self, fromData: str) -> str:
        if len(self.data) == 0:
            return ""
        return str(self.data)
