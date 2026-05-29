from typing import Dict
from upgrades import Upgrade
from player import Player

class GameCore:
    def __init__(self):
        self.player = Player()
        self.upgrades: Dict[str, Upgrade] = self._init_upgrades()
        self.base_click_power = 1.0

    @property
    def ascension_threshold(self) -> float:
        # The amount of little lathams needed to perform an ascension, increasing with each ascension.
        return 100000 * (1.5 ** self.player.ascensions)

    def _init_upgrades(self) -> dict[str, Upgrade]:
        return {
            "Beef Tallow Moisturiser": Upgrade("Beef Tallow Moisturiser", 10, 1.15, "click", 0.5),
            "Sea Salt Spray": Upgrade("Sea Salt Spray", 100, 1.15, "idle", 1.0),
            "Tear Maxxing": Upgrade("Tear Maxxing", 1000, 1.15, "idle", 12.0),
            "Ice Roller": Upgrade("Ice Roller", 5000, 1.15, "idle", 50.0),
            "Vitamin C Serum": Upgrade("Vitamin C Serum", 20000, 1.15, "idle", 200.0),
        }
        
    @property
    def current_click_power(self) -> float:
        upgrade_bonus = sum(upg.total_bonus for upg in self.upgrades.values() if upg.effect_type == "click")
        return (self.base_click_power + upgrade_bonus) * self.player.ascensions_multiplier
    
    @property
    def current_idle_power(self) -> float:
        upgrade_bonus = sum(upg.total_bonus for upg in self.upgrades.values() if upg.effect_type == "idle")
        return upgrade_bonus * self.player.ascensions_multiplier
    
    def click(self):
        self.player.little_lathams += self.current_click_power
        
    def idle(self, delta_time: float):
        self.player.little_lathams += self.current_idle_power * delta_time
        
    def attempt_purchase(self, upgrade_name: str) -> bool:
        if upgrade_name in self.upgrades:
            upgrade = self.upgrades[upgrade_name]
            if self.player.little_lathams >= upgrade.current_cost:
                self.player.little_lathams -= upgrade.current_cost
                upgrade.level_up()
                return True
        return False
    
    def attempt_ascension(self) -> bool:
        if self.player.little_lathams >= self.ascension_threshold:
            self.player.ascension_reset()
            for upgrade in self.upgrades.values():
                upgrade.reset()
            return True
        return False