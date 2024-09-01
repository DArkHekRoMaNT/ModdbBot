import io
import json
import logging
import os.path
import threading

from . import discord_bot, api, utils
from .api.models import *

logger = logging.getLogger("subscription")


class SubscribedUser:
    moddb_name_cached: str = ""
    moddb_mods_cached: list[ModSlim] = []

    def __init__(self, data: dict):
        self.discord_user_id = int(data.get("discord_user_id"))
        self.moddb_user_id = int(data.get("moddb_user_id", -1))
        self.moddb_extra_mods = list[int](data.get("moddb_extra_mods", []))  # List of asset_id
        self.custom_words = list[int](data.get("moddb_subscriptions", []))  # Custom words for search
        self.all_mod_mentions = bool(data.get("all_mod_mentions", False))
        self.skip_logs = bool(data.get("skip_logs", False))


class SubscriptionManager:
    def __init__(self):
        self.filename = utils.get_datapath(subdir="data", filename="subscriptions.json")
        self.users_lock = threading.Lock()
        self.users = self._load()
        self._save()

    def update(self):
        self.users_lock.acquire()
        for user in self.users.values():
            try:
                user.moddb_name_cached = api.get_author(user.moddb_user_id).name
                user.moddb_mods_cached = api.get_mods(author_id=user.moddb_user_id)
            except KeyError:  # Wrong user id
                logger.warning(f"Wrong user id {user.moddb_user_id}")
                pass
        self.users_lock.release()

    def on_new_comment(self, comment: Comment):
        self.users_lock.acquire()
        for user in self.users.values():
            if self._is_suited(user, comment):
                splitter = "mio3qj19inq1oiv14io1j"
                comment.text = (
                    comment.text

                    .replace("<p>", "").replace("</p>", "")
                    .replace("<span class=\"mention username\">", "@").replace("</span>", "")
                    .replace("<br />", "\n")
                    .replace("&nbsp;", " ")
                    .replace("\n<ul>", "").replace("\n</ul>", "")
                    .replace("<ul>", "").replace("</ul>", "")
                    .replace("<li>", "  - ").replace("</li>", "")
                    .replace("<div>", "").replace("</div>", "")

                    .replace("Critical error occurred in the following mod:", splitter)
                    .replace("Running on 64 bit ", splitter)
                    .replace("\n" + splitter, splitter)
                    .replace("\n" + splitter, splitter)
                    .replace("\n" + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(splitter, " **CRASHLOG** " + splitter)
                    .split(splitter)[0]

                    .replace("Mods, sorted by dependency: ", splitter)
                    .replace("\n" + splitter, splitter)
                    .replace("\n" + splitter, splitter)
                    .replace("\n" + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(" " + splitter, splitter)
                    .replace(splitter, " **LOGS** " + splitter)
                    .split(splitter)[0]
                )

                if user.skip_logs and not self._is_suited(user, comment):
                    continue

                discord_bot.send_comment(user.discord_user_id, comment)
        self.users_lock.release()

    @staticmethod
    def _is_suited(user: SubscribedUser, comment: Comment) -> bool:
        if comment.user_id == user.moddb_user_id:
            return False

        if user.moddb_name_cached and comment.text.__contains__(user.moddb_name_cached):
            return True

        for mod in user.moddb_mods_cached:
            if mod.asset_id == comment.asset_id:
                return True

        for asset_id in user.moddb_extra_mods:
            if asset_id == comment.asset_id:
                return True

        if user.all_mod_mentions:
            for line in user.moddb_mods_cached:
                if comment.text.__contains__(line):
                    return True

        for line in user.custom_words:
            if comment.text.__contains__(line):
                return True

    def update_user(self, user: SubscribedUser) -> None:
        self.users_lock.acquire()
        self.users[user.discord_user_id] = user
        self._save()
        self.users_lock.release()

    def get_user(self, discord_user_id: int) -> SubscribedUser:
        self.users_lock.acquire()
        user = self.users.get(discord_user_id, SubscribedUser({"discord_user_id": discord_user_id}))
        self.users_lock.release()
        return user

    def _load(self):
        try:
            s_users = dict[int, SubscribedUser]()
            if os.path.exists(self.filename):
                with io.open(self.filename, "r", encoding="utf-8") as file:
                    json_users = dict[str, dict](json.loads(file.read()))
                    for key in json_users:
                        su = SubscribedUser(json_users[key])
                        s_users[su.discord_user_id] = su
            return s_users
        except (FileNotFoundError, json.JSONDecodeError):
            return dict[int, SubscribedUser]()

    def _save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with io.open(self.filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(self.users, cls=SubscribedUserEncoder, indent=2))


class SubscribedUserEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SubscribedUser):
            return dict([(key, value) for key, value in o.__dict__.items() if "cached" not in key])
        return json.JSONEncoder.default(self, o)
