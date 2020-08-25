import unittest
import pymcws as mcws

"""
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!!!!!!!                      !!!!!!!!!!
    !!!!!!!!        WARNING       !!!!!!!!!!
    !!!!!!!!                      !!!!!!!!!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    DO NOT RUN THESE TESTS ON YOUR MEDIA SERVER!
    These tests are destructive, and WILL modify or delete your database.
    To migitate risks, all tests check for certain conditions:
    - The setUp method connects to a server with a key of your choice, which
      should be set up with the username/password test/test
    - The setup method tests whether a library called "Test" is loaded
      and fails otherwise.
"""


class TestLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = mcws.get_media_server("vqgcdx", "test", "test")
        assert cls.server.library.get_loaded()["Name"], "Test"
        cls.file = cls.server.files.search("[Name]=Ukulele", "MPL")

    def setUp(self):
        self.server.playback.set_playlist(self.file)

    def test_set_info(self):
        print("passing time")
        pass

    @classmethod
    def tearDownClass(self):
        self.server.session.close()


if __name__ == "__main__":
    unittest.main()
