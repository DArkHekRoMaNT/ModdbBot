from datetime import datetime, timezone


class Model:
    @staticmethod
    def get_date(date: str) -> datetime:
        if date:
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
