from typing import List

from main import TestCase


class TestRequests(TestCase):
    def test_get_mod(self):
        get_mod(2)

    def test_get_mods(self):
        def check(mods: List[ModSlim]):
            self.assertIsNotNone(mods)
            # print([vars(x) for x in mods])

        check(get_mods())
        check(get_mods(author_id=10))
        check(get_mods(text="tests"))
        check(get_mods(tag_ids=[1, 2]))
        check(get_mods(tag_ids=[-1]))
        check(get_mods(author_id=-1))
        check(get_mods(asc=True))
        check(get_mods(order_by=SortModBy.FOLLOWS))
        check(get_mods(order_by=SortModBy.ASSET_CREATED))
        check(get_mods(game_versions=["1.14.1"]))

    def test_get_changelogs(self):
        get_changelogs(100)

    def test_get_tags(self):
        get_tags()

    def test_get_authors(self):
        get_authors()

    def test_get_comments(self):
        get_comments()
        get_comments(10)

    def test_get_game_versions(self):
        get_game_versions()
