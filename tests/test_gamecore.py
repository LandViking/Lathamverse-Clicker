import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch

from gamecore import GameCore


class TestAscensionThreshold(unittest.TestCase):
    def test_threshold_scales_with_ascension_count(self):
        core = GameCore()
        base = core.ascension_threshold
        core.player.ascensions = 1
        self.assertAlmostEqual(core.ascension_threshold, base * 2.5)


class TestClick(unittest.TestCase):
    def setUp(self):
        self.core = GameCore()

    def test_click_returns_none_when_on_cooldown(self):
        first = self.core.click()
        self.assertIsNotNone(first)
        second = self.core.click()
        self.assertIsNone(second)

    def test_click_adds_power_to_currency(self):
        before = self.core.player.little_lathams
        power, is_crit = self.core.click()
        self.assertFalse(is_crit)
        self.assertEqual(self.core.player.little_lathams, before + power)
        self.assertEqual(self.core.player.total_lathams_earned, power)

    def test_crit_click_multiplies_power_and_is_reported(self):
        self.core.prestige_upgrades["Critical Clicks"].purchased = True
        with patch("gamecore.random.random", return_value=0.0):
            power, is_crit = self.core.click()
        self.assertTrue(is_crit)
        self.assertAlmostEqual(power, self.core.current_click_power * 5.0)


class TestIdle(unittest.TestCase):
    def test_idle_adds_income_proportional_to_time(self):
        core = GameCore()
        core.upgrades["Sea Salt Spray"].level = 4  # idle upgrade, base_power 1.0
        idle_power = core.current_idle_power
        core.idle(2.0)
        self.assertAlmostEqual(core.player.little_lathams, idle_power * 2.0)
        self.assertAlmostEqual(core.player.total_lathams_earned, idle_power * 2.0)


class TestPurchases(unittest.TestCase):
    def setUp(self):
        self.core = GameCore()

    def test_purchase_fails_when_unaffordable(self):
        self.assertFalse(self.core.attempt_purchase("Beef Tallow Moisturiser"))
        self.assertEqual(self.core.upgrades["Beef Tallow Moisturiser"].level, 0)

    def test_purchase_succeeds_and_deducts_cost(self):
        upgrade = self.core.upgrades["Beef Tallow Moisturiser"]
        self.core.player.little_lathams = upgrade.current_cost
        self.assertTrue(self.core.attempt_purchase("Beef Tallow Moisturiser"))
        self.assertEqual(upgrade.level, 1)
        self.assertEqual(self.core.player.little_lathams, 0)

    def test_purchase_blocked_by_ascension_gate(self):
        # Gua Sha requires 1 ascension
        self.core.player.little_lathams = 10_000_000
        self.assertFalse(self.core.attempt_purchase("Gua Sha"))

    def test_bulk_buy_purchases_multiple_levels_at_once(self):
        self.core.prestige_upgrades["Bulk Buy"].purchased = True
        upgrade = self.core.upgrades["Beef Tallow Moisturiser"]
        # Costs (base 15, scaling 1.18) for levels 0-2 sum to 53.586; enough for
        # exactly 3 levels but not a 4th (which needs 24.645 more).
        self.core.player.little_lathams = 60.0
        self.core.attempt_purchase("Beef Tallow Moisturiser")
        self.assertEqual(upgrade.level, 3)


class TestAscension(unittest.TestCase):
    def setUp(self):
        self.core = GameCore()

    def test_ascension_fails_below_threshold(self):
        self.core.player.little_lathams = self.core.ascension_threshold - 1
        self.assertFalse(self.core.attempt_ascension())
        self.assertEqual(self.core.player.ascensions, 0)

    def test_ascension_resets_currency_and_upgrades_and_grants_ap(self):
        self.core.player.little_lathams = self.core.ascension_threshold
        self.core.upgrades["Beef Tallow Moisturiser"].level = 5
        self.assertTrue(self.core.attempt_ascension())
        self.assertEqual(self.core.player.ascensions, 1)
        self.assertEqual(self.core.player.little_lathams, 0)
        self.assertEqual(self.core.upgrades["Beef Tallow Moisturiser"].level, 0)
        self.assertGreaterEqual(self.core.player.ascension_points, 1)

    def test_ascension_applies_starting_bonus_from_prestige(self):
        self.core.prestige_upgrades["Starting Bonus"].purchased = True
        self.core.player.little_lathams = self.core.ascension_threshold
        self.core.attempt_ascension()
        self.assertEqual(self.core.player.little_lathams, 50.0)

    def test_calculate_ap_reward_is_zero_below_threshold(self):
        self.core.player.little_lathams = 0
        self.assertEqual(self.core.calculate_ap_reward(), 0)

    def test_calculate_ap_reward_grows_with_overshoot(self):
        self.core.player.little_lathams = self.core.ascension_threshold
        reward_at_threshold = self.core.calculate_ap_reward()
        self.core.player.little_lathams = self.core.ascension_threshold * 8
        reward_after_overshoot = self.core.calculate_ap_reward()
        self.assertGreater(reward_after_overshoot, reward_at_threshold)


class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_load_round_trip(self):
        core = GameCore()
        core.player.little_lathams = 500
        core.player.ascensions = 2
        core.player.ascension_points = 7
        core.upgrades["Beef Tallow Moisturiser"].level = 3
        core.prestige_upgrades["Starting Bonus"].purchased = True
        core.save_game(self.path)

        loaded = GameCore()
        self.assertTrue(loaded.load_game(self.path))
        self.assertEqual(loaded.player.ascensions, 2)
        self.assertEqual(loaded.player.ascension_points, 7)
        self.assertEqual(loaded.upgrades["Beef Tallow Moisturiser"].level, 3)
        self.assertTrue(loaded.prestige_upgrades["Starting Bonus"].purchased)

    def test_load_missing_file_returns_false(self):
        core = GameCore()
        self.assertFalse(core.load_game("/nonexistent/path/savegame.json"))

    def test_offline_earnings_added_to_lifetime_total(self):
        data = {
            "little_lathams": 100.0,
            "ascensions": 0,
            "ascension_points": 0,
            "total_lathams_earned": 100.0,
            "upgrades": {"Sea Salt Spray": 5},
            "prestige_purchased": [],
            "last_save_time": time.time() - 100,
        }
        with open(self.path, "w") as f:
            json.dump(data, f)

        core = GameCore()
        core.load_game(self.path)

        self.assertGreater(core.offline_lathams_gained, 0)
        self.assertAlmostEqual(
            core.player.little_lathams,
            100.0 + core.offline_lathams_gained,
        )
        self.assertAlmostEqual(
            core.player.total_lathams_earned,
            100.0 + core.offline_lathams_gained,
        )


if __name__ == "__main__":
    unittest.main()
