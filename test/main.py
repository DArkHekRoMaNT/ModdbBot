import logging
import unittest

from dotenv import load_dotenv

from moddb_bot.logger import setup_logger

HARD_MODE = False
_prepared = False


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global _prepared
        if _prepared:
            return
        _prepared = True
        load_dotenv()
        setup_logger()
        logging.getLogger("test").setLevel(logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
