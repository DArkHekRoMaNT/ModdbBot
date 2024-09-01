import logging
import unittest

from dotenv import load_dotenv

from src.moddb_bot import setup_logger

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
        logging.getLogger("tests").setLevel(logging.DEBUG)


if __name__ == '__main__':
    unittest.main()
