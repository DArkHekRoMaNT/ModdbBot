from .Model import Model


class Tag(Model):
    def __init__(self, data: dict) -> None:
        self.tag_id = int(data.get("tagid"))
        self.name = str(data.get("name"))
        self.color = str(data.get("color"))


class GameVersion(Tag):
    pass
