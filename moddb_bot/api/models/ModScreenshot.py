from .Model import Model


class ModScreenshot(Model):
    def __init__(self, data: dict) -> None:
        self.file_id = int(data.get("fileid"))
        self.main_file = str(data.get("mainfile"))
        self.filename = str(data.get("filename"))
        self.thumbnail_filename = str(data.get("thumbnailfilename"))
        self.created = self.get_date(data.get("created"))
