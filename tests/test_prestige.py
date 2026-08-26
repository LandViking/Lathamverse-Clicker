import unittest

from prestige import PrestigeUpgrade, create_prestige_upgrades


class TestPrestigeUpgrade(unittest.TestCase):
    def setUp(self):
        self.upgrade = PrestigeUpgrade("Test Prestige", cost=3, description="desc",
                                        effect_key="click_mult", effect_value=0.5,
                                        required_ascensions=2)

    def test_cannot_purchase_below_required_ascensions(self):
        self.assertFalse(self.upgrade.can_purchase(ap=10, ascensions=1))

    def test_cannot_purchase_without_enough_ap(self):
        self.assertFalse(self.upgrade.can_purchase(ap=2, ascensions=2))

    def test_can_purchase_when_affordable_and_unlocked(self):
        self.assertTrue(self.upgrade.can_purchase(ap=3, ascensions=2))

    def test_cannot_purchase_twice(self):
        self.assertTrue(self.upgrade.can_purchase(ap=3, ascensions=2))
        self.upgrade.purchase()
        self.assertFalse(self.upgrade.can_purchase(ap=3, ascensions=2))

    def test_purchase_marks_purchased_and_returns_cost(self):
        cost = self.upgrade.purchase()
        self.assertEqual(cost, 3)
        self.assertTrue(self.upgrade.purchased)


class TestCreatePrestigeUpgrades(unittest.TestCase):
    def test_returns_unique_named_upgrades(self):
        upgrades = create_prestige_upgrades()
        self.assertGreater(len(upgrades), 0)
        for name, upgrade in upgrades.items():
            self.assertEqual(upgrade.name, name)
            self.assertFalse(upgrade.purchased)


if __name__ == "__main__":
    unittest.main()
