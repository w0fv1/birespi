class BaseConfig:
    def __init__(self) -> None:
        pass

    def toJson(self) -> dict:
        raise NotImplementedError
    
    def set(self, key: str, value: any):
        setattr(self, key, value)