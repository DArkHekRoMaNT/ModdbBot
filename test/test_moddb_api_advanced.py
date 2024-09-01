import logging
import unittest

from moddb_bot.api import *
from main import TestCase, HARD_MODE

logger = logging.getLogger("test")


class TestRequests(TestCase):
    @unittest.skipUnless(HARD_MODE, "Too large")
    def test_get_every_mod(self):
        logger.info(f"Get every mod test")
        mods = get_mods()
        i = 0
        for mod in mods:
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(mods)-1}")
            i += 1
            get_mod(mod.mod_id)
