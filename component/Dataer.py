import os


class BaseDataer:

    def __init__(self) -> None:
        pass

    def loadDatas(self, dataPath: str):
        pass

    def loadData(self, filename: str):
        pass

    async def getSimilarity(self, fromData: str):
        pass

    def getDataFiles(self) -> list[str]:
        pass

    def getData(self, filename: str) -> str:
        pass

    def updateData(self, filename: str, content: str):
        pass

    def uploadData(self, filename: str, content: str) -> str:
        pass

    def deleteData(self, filename: str):
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
        self.loadDatas()

    def loadDatas(self):
        self.data = {}
        # 读取dataPath文件夹下所有文件的内容，存入self.data

        for file in os.listdir(self.config.dataPath):
            print(type(file), file)
            self.loadData(file)

    def loadData(self, filename: str):
        with open(f"{self.config.dataPath}/{filename}", "r") as f:
            content: str = f.read()
            self.data[filename] = content

    def watchFile(self, filename: str):
        pass

    async def getSimilarity(self, fromData: str) -> str:
        if len(self.data) == 0:
            return ""
        return str(self.data)

    def getDataFiles(self) -> list[str]:
        return os.listdir(self.config.dataPath)

    def getData(self, filename: str) -> str:
        with open(f"{self.config.dataPath}/{filename}", "r") as f:
            return f.read()

    def updateData(self, filename: str, content: str) -> str:
        with open(f"{self.config.dataPath}/{filename}", "w") as f:
            f.write(content)
            self.loadData(filename)

    def uploadData(self, filename: str, content: str) -> str:
        with open(f"{self.config.dataPath}/{filename}", "w") as f:
            f.write(content)
            self.loadData(filename)

    def deleteData(self, filename: str):
        os.remove(f"{self.config.dataPath}/{filename}")
        self.data.pop(filename)
