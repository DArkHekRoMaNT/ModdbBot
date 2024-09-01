from .Model import Model


class Comment(Model):
    def __init__(self, data: dict) -> None:
        self.comment_id = int(data.get("commentid"))
        self.asset_id = int(data.get("assetid"))
        self.user_id = int(data.get("userid"))
        self.text = str(data.get("text"))
        self.created = self.get_date(data.get("created"))
        self.last_modified = self.get_date(data.get("lastmodified"))
