from .Model import Model


class ModRelease(Model):
    def __init__(self, data: dict) -> None:
        self.release_id = int(data.get("releaseid"))
        self.main_file = str(data.get("mainfile"))
        self.filename = str(data.get("filename"))
        self.file_id = int(data.get("fileid") if data.get("fileid") else -1)
        self.downloads = int(data.get("downloads"))
        self.game_versions = list[str](data.get("tags"))
        self.mod_id_string = list[str](data.get("modidstr") if data.get("modidstr") else [])
        self.mod_version = str(data.get("modversion"))
        self.created = self.get_date(data.get("created"))
