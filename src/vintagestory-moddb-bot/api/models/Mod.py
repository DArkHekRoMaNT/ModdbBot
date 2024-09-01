from .ModRelease import ModRelease
from .ModScreenshot import ModScreenshot
from .ModSide import ModSide
from .ModType import ModType
from .Model import Model


class Mod(Model):
    def __init__(self, data: dict) -> None:
        self.mod_id = int(data.get("modid"))
        self.asset_id = int(data.get("assetid"))
        self.name = str(data.get("name"))
        self.text = str(data.get("text"))
        self.author = str(data.get("author"))
        self.url_alias = str(data.get("urlalias"))
        self.logo_filename = str(data.get("logofilename"))
        self.logo_file = str(data.get("logofile"))
        self.home_page_url = str(data.get("homepageurl"))
        self.source_code_url = str(data.get("sourcecodeurl"))
        self.trailer_video_url = str(data.get("trailervideourl"))
        self.issue_tracker_url = str(data.get("issuetrackerurl"))
        self.wiki_url = str(data.get("wikiurl"))
        self.downloads = int(data.get("downloads"))
        self.follows = int(data.get("follows"))
        self.trending_points = int(data.get("trendingpoints"))
        self.comments = int(data.get("comments"))
        self.side = ModSide(data.get("side"))
        self.type = ModType(data.get("type"))
        self.created = self.get_date(data.get("created"))
        self.last_modified = self.get_date(data.get("lastmodified"))
        self.tags = list[str](data.get("tags"))
        self.releases = list[ModRelease]([ModRelease(x) for x in data.get("releases")])
        self.screenshots = list[ModScreenshot]([ModScreenshot(x) for x in data.get("screenshots")])
