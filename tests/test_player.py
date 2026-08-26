import unittest

from player import Player


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player()

    def test_initial_state(self):
        self.assertEqual(self.player.little_lathams, 0)
        self.assertEqual(self.player.ascensions, 0)
        self.assertEqual(self.player.ascension_points, 0)
        self.assertEqual(self.player.total_lathams_earned, 0)

    def test_ascensions_multiplier_grows_exponentially(self):
        self.assertEqual(self.player.ascensions_multiplier, 1.0)
        self.player.ascensions = 1
        self.assertEqual(self.player.ascensions_multiplier, 1.5)
        self.player.ascensions = 2
        self.assertEqual(self.player.ascensions_multiplier, 2.25)

    def test_ascension_reset_increments_count_and_clears_currency(self):
        self.player.little_lathams = 1_000_000
        self.player.ascension_reset()
        self.assertEqual(self.player.ascensions, 1)
        self.assertEqual(self.player.little_lathams, 0)

    def test_ascension_reset_does_not_touch_ap_or_lifetime_stats(self):
        self.player.ascension_points = 5
        self.player.total_lathams_earned = 12345
        self.player.ascension_reset()
        self.assertEqual(self.player.ascension_points, 5)
        self.assertEqual(self.player.total_lathams_earned, 12345)


if __name__ == "__main__":
    unittest.main()
