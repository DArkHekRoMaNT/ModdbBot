from .Model import Model


class Changelog(Model):
    def __init__(self, data: dict) -> None:
        self.changelog_id = int(data.get("changelogid"))
        self.asset_id = int(data.get("assetid"))
        self.user_id = int(data.get("userid"))
        self.text = str(data.get("text"))
        self.created = self.get_date(data.get("created"))
        self.last_modified = self.get_date(data.get("lastmodified"))
