import io
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import List

from dotenv import load_dotenv

from .discord_bot import run as run_discord_bot, send_notify
from .api import api
from .api.models import *
from .logger import setup_logger
from .subscription import SubscriptionManager
from .utils import get_datapath

logger = logging.getLogger("bot")


class ModdbBot:
    def __init__(self, subs: SubscriptionManager):
        self.filename = get_datapath(subdir="data", filename="last_update_time.txt")
        self.mod_cache = dict[int, int]()
        self.last_update_time = self._load()
        self.current_time = self.utcnow()
        self.subs = subs
        logger.info(f"Started")
        logger.info(f"Last update time {self.utcnow() - self.last_update_time} ago")

        slim_data = [dict({
            "name": x.name,
            "mod_id": x.mod_id,
            "author": x.author,
            "comments": x.comments,
            "downloads": x.downloads,
            "follows": x.follows,
            "trending_points": x.trending_points
        }) for x in api.get_mods()]

        fn = get_datapath(subdir="data", filename="mods.json")
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        with io.open(fn, "w", encoding="utf-8") as file:
            file.write(json.dumps(slim_data))

    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(tz=timezone.utc)

    def run(self):
        while True:
            self.current_time = self.utcnow()
            self.subs.update()
            self.tick()
            self.last_update_time = self.current_time
            self._save()
            send_notify("Checked")
            logger.info("Sleep")
            time.sleep(60 * 5)

    def tick(self):
        logger.info("Wake up")
        has_old = False
        comments = api.get_comments()
        for comment in comments:
            if comment.created < self.last_update_time:
                has_old = True

        if has_old:
            logger.info("New comments lesser than 100")
            self.check_updates(comments)
        else:
            logger.info("Too many new comments")
            mods = api.get_mods(order_by=SortModBy.COMMENTS)
            total_loaded = 0
            i = 0
            for mod in mods:
                if i % 50 == 0:
                    logger.debug(f"Progress: {i}/{len(mods) - 1}, loaded {total_loaded}")
                i += 1
                if self.mod_cache.get(mod.mod_id) == mod.comments:
                    continue  # No new comments, skipped
                if mod.comments == 0:
                    break  # No comments, stopped
                total_loaded += 1
                self.mod_cache[mod.mod_id] = mod.comments
                mod_comments = api.get_comments(mod.asset_id)
                self.check_updates(mod_comments)
            logger.info(f"Summary: {total_loaded}/{len(mods) - 1} mods updated")

    def check_updates(self, comments: List[Comment]):
        comments.reverse()
        for comment in comments:
            if comment.created > self.last_update_time:
                self.subs.on_new_comment(comment)

    def _load(self):
        try:
            with io.open(self.filename, "r", encoding="utf-8") as file:
                return datetime.fromtimestamp(float(file.read()), tz=timezone.utc)
        except (FileNotFoundError, Exception):
            return self.utcnow() - timedelta(hours=24)

    def _save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with io.open(self.filename, "w", encoding="utf-8") as file:
            file.write(self.last_update_time.timestamp().__str__())


if __name__ == '__main__':
    load_dotenv()
    setup_logger()
    token = os.getenv("DISCORD_TOKEN")
    subscription = SubscriptionManager()
    threading.Thread(target=run_discord_bot, args=[token, subscription]).start()
    ModdbBot(subscription).run()
