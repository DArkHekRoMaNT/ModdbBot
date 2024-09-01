import logging
from typing import List

import requests

from .models import *

logger = logging.getLogger("api")

BASE_URL = "http://mods.vintagestory.at/api"
users_cached = dict[int, Author]()


def _get_raw(path: str) -> dict or list or None:
    url = f"{BASE_URL}/{path}"
    logger.log(logging.TRACE,f"Request to {url}")
    response = requests.get(url)
    data = dict(response.json())
    if data.get("statuscode") == "200":
        logger.log(logging.TRACE,f"Response: OK 200")
        # Drop status code, get only data
        data.pop("statuscode")
        return data.popitem()[1]
    logger.error(f"Response: Error {data.get('statuscode')}")
    return None


def get_tags() -> List[Tag]:
    return [Tag(x) for x in _get_raw("tags")]


def get_game_versions() -> List[GameVersion]:
    return [GameVersion(x) for x in _get_raw("gameversions")]


def get_authors() -> List[Author]:
    return [Author(x) for x in _get_raw("authors")]


def get_author(user_id: int) -> Author:
    global users_cached
    if users_cached.__contains__(user_id):
        return users_cached[user_id]
    logger.debug(f"No cached author {user_id}, need update")
    users_cached = dict([(x.user_id, x) for x in get_authors()])
    return users_cached[user_id]


def get_comments(asset_id: int = None) -> List[Comment]:
    if asset_id is None:
        return [Comment(x) for x in _get_raw("comments")]
    return [Comment(x) for x in _get_raw(f"comments/{asset_id}")]


def get_changelogs(asset_id: int) -> List[Changelog]:
    return [Changelog(x) for x in _get_raw(f"changelogs/{asset_id}")]


def get_mods(*,
             tag_ids: List[int] = None,
             game_versions: List[str] = None,
             author_id: int = None,
             text: str = None,
             order_by: SortModBy = None,
             asc: bool = False) -> List[ModSlim]:

    extra: list[str] = []
    if tag_ids:
        for tag_id in tag_ids:
            extra.append(f"tagids[]={tag_id}")

    if game_versions:
        for game_version in game_versions:
            extra.append(f"gameversions[]={game_version}")

    if author_id:
        extra.append(f"author={author_id}")

    if text:
        extra.append(f"text={text}")

    if order_by:
        extra.append(f"orderby={order_by.value}")

    if asc:
        extra.append(f"orderdirection=asc")

    return [ModSlim(x) for x in _get_raw("mods" if len(extra) == 0 else f"mods?{'&'.join(extra)}")]


def get_mod(mod_id: int) -> Mod:
    return Mod(_get_raw(f"mod/{mod_id}"))


def get_mod_by_asset_id(asset_id: int) -> ModSlim:
    for mod in get_mods():
        if mod.asset_id == asset_id:
            return mod
    raise Exception(f"Unknown asset id {asset_id}")


def search_author(name: str, case_sensitive=True) -> Author:
    for author in get_authors():
        if case_sensitive:
            if author.name == name:
                return author
        elif author.name.lower() == name.lower():
            return author

