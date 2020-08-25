import unittest
import pymcws as mcws
import time

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

    Additionally, this tests requires the following file to be in the library:
    https://www.dropbox.com/s/lgkb6jd82xngqvh/Ukulele%20Song.mp3?dl=1
"""


class TestPlayback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = mcws.get_media_server("vqgcdx", "test", "test")
        assert cls.server.library.get_loaded()["Name"], "Test"
        cls.file = cls.server.files.search("[Name]=Ukulele", "MPL")

    def setUp(self):
        self.server.playback.set_playlist(self.file)
        self.server.playback.stop()

    def test_info(self):
        info = self.server.playback.info()
        # print(info)
        self.assertEqual(info["Name"], "Ukulele Song")
        self.assertEqual(info["Artist"], "Rafael Krux")
        self.assertEqual(info["NextFileKey"], -1)
        self.assertEqual(info["State"], 0)

    def test_playback_command(self):
        self.assertEqual(self.server.playback.info()["State"], 0)
        self.server.playback.play()
        time.sleep(2)
        self.assertEqual(self.server.playback.info()["State"], 2)
        self.server.playback.pause()
        time.sleep(1)
        self.assertEqual(self.server.playback.info()["State"], 1)
        self.server.playback.playpause()
        time.sleep(1)
        self.assertEqual(self.server.playback.info()["State"], 2)
        self.server.playback.playpause()
        time.sleep(1)
        self.assertEqual(self.server.playback.info()["State"], 1)
        self.server.playback.stop()
        time.sleep(2)
        self.assertEqual(self.server.playback.info()["State"], 0)

    def test_mute(self):
        self.assertEqual(self.server.playback.mute(True), True)
        self.assertEqual(self.server.playback.mute(), True)
        self.assertEqual(self.server.playback.mute(False), False)
        self.assertEqual(self.server.playback.mute(), False)
        self.assertEqual(self.server.playback.mute(True), True)
        self.assertEqual(self.server.playback.mute(), True)

    def test_repeat(self):
        self.assertEqual(self.server.playback.repeat("Track"), "Track")
        self.assertEqual(self.server.playback.repeat(), "Track")
        self.assertEqual(self.server.playback.repeat(False), "Off")
        self.assertEqual(self.server.playback.repeat(), "Off")
        self.assertEqual(self.server.playback.repeat("Playlist"), "Playlist")
        self.assertEqual(self.server.playback.repeat(), "Playlist")
        self.assertEqual(self.server.playback.repeat("Track"), "Track")
        self.assertEqual(self.server.playback.repeat(), "Track")
        self.assertEqual(self.server.playback.repeat("Stop"), "Stop")
        self.assertEqual(self.server.playback.repeat(), "Stop")
        self.assertEqual(self.server.playback.repeat("Off"), "Off")
        self.assertEqual(self.server.playback.repeat(), "Off")
        self.assertEqual(self.server.playback.repeat("Track"), "Track")
        self.assertEqual(self.server.playback.repeat(), "Track")
        self.assertEqual(self.server.playback.repeat(False), "Off")
        self.assertEqual(self.server.playback.repeat(), "Off")

    def test_volume(self):
        self.assertEqual(self.server.playback.volume(0), 0)
        self.assertEqual(self.server.playback.volume(0.5), 0.5)
        self.assertEqual(self.server.playback.volume(1), 1)
        self.assertEqual(
            self.server.playback.volume(return_display_string=True), "100%  (+0.0 dB)"
        )
        self.assertEqual(self.server.playback.volume(-0.1, relative=True), 0.9)
        self.assertEqual(self.server.playback.volume(0.05, relative=True), 0.95)

    @classmethod
    def tearDownClass(self):
        self.server.session.close()


if __name__ == "__main__":
    unittest.main()
