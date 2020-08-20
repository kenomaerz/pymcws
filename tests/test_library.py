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

    def setUp(self):
        pass

    def test_library_list(self):
        libraries = self.server.library.get_list()
        libraries_with_header = self.server.library.get_list(True)
        self.assertEqual(libraries, libraries_with_header[1:])
        self.assertEqual(len(libraries_with_header[0]), 2)
        self.assertEqual(libraries_with_header[0]["NumberOfLibraries"], len(libraries))
        self.assertIsInstance(libraries_with_header[0]["DefaultLibrary"], int)
        for library in libraries:
            self.assertEqual(len(library), 4)

    def test_library_get_defaul(self):
        header = self.server.library.get_list(True)[0]
        default = self.server.library.get_default()
        self.assertEqual(header["DefaultLibrary"], default["ID"])

    def test_library_get_loaded(self):
        loaded = self.server.library.get_loaded()
        self.assertTrue(loaded["Loaded"])

    @classmethod
    def tearDownClass(self):
        self.server.session.close()


if __name__ == "__main__":
    unittest.main()
