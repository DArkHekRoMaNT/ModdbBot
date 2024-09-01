from .ModSide import ModSide
from .ModType import ModType
from .Model import Model


class ModSlim(Model):
    def __init__(self, data: dict) -> None:
        self.mod_id = int(data.get("modid"))
        self.asset_id = int(data.get("assetid"))
        self.name = str(data.get("name"))
        self.downloads = int(data.get("downloads"))
        self.follows = int(data.get("follows"))
        self.trending_points = int(data.get("trendingpoints"))
        self.comments = int(data.get("comments"))
        self.summary = str(data.get("summary"))
        self.mod_id_strings = list[str](data.get("modidstrs"))
        self.author = str(data.get("author"))
        self.url_alias = str(data.get("urlalias"))
        self.side = ModSide(data.get("side"))
        self.type = ModType(data.get("type"))
        self.logo = str(data.get("logo"))
        self.tags = list[str](data.get("tags"))
        self.last_released = self.get_date(data.get("lastreleased"))
