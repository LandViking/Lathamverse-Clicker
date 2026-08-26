import unittest

from upgrades import Upgrade


class TestUpgrade(unittest.TestCase):
    def setUp(self):
        self.upgrade = Upgrade("Test Upgrade", base_cost=100, scaling=1.2,
                                effect_type="click", base_power=5.0, required_ascensions=0)

    def test_starts_at_level_zero(self):
        self.assertEqual(self.upgrade.level, 0)
        self.assertEqual(self.upgrade.total_bonus, 0)

    def test_current_cost_scales_with_level(self):
        self.assertEqual(self.upgrade.current_cost, 100)
        self.upgrade.level_up()
        self.assertAlmostEqual(self.upgrade.current_cost, 120)
        self.upgrade.level_up()
        self.assertAlmostEqual(self.upgrade.current_cost, 144)

    def test_total_bonus_scales_linearly_with_level(self):
        self.upgrade.level_up()
        self.upgrade.level_up()
        self.upgrade.level_up()
        self.assertEqual(self.upgrade.total_bonus, 15.0)

    def test_reset_returns_to_level_zero(self):
        self.upgrade.level_up()
        self.upgrade.level_up()
        self.upgrade.reset()
        self.assertEqual(self.upgrade.level, 0)
        self.assertEqual(self.upgrade.total_bonus, 0)
        self.assertEqual(self.upgrade.current_cost, 100)


if __name__ == "__main__":
    unittest.main()
