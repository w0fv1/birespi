from pydantic import BaseModel


class LiveRoomInfo(BaseModel):
    roomId: int = 0
    uname: str = ""
    uavatar: str = ""
    uid: int = 0
    title: str = ""
    cover: str = ""

    def __str__(self):
        return f"roomId:{self.roomId}, uname:{self.uname}, uavatar:{self.uavatar}, uid:{self.uid}, title:{self.title}, cover:{self.cover}"
