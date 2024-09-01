from .Model import Model


class Author(Model):
    def __init__(self, data: dict) -> None:
        self.user_id = int(data.get("userid"))
        self.name = str(data.get("name"))
