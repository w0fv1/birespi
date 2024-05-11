class Danmu:
    content: str
    username: str

    def __init__(self, username: str, content: str):
        self.content = content
        self.username = username
