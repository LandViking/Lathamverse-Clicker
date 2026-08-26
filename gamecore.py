import json
import math
import os
import random
import time
from typing import Dict
from upgrades import Upgrade
from player import Player
from prestige import PrestigeUpgrade, create_prestige_upgrades

# Maximum offline time that counts for idle earnings (30 minutes)
MAX_OFFLINE_SECONDS = 1800

# Milestone definitions: (ascension_count, name, description)
MILESTONES = [
    (1, "The Great Reset", "Ascend for the first time"),
    (2, "Enlightened", "Reach ascension 2"),
    (3, "Transcendent", "Reach ascension 3"),
    (5, "Latham Demigod", "Reach ascension 5"),
    (8, "Latham Legend", "Reach ascension 8"),
    (10, "Eternal Latham", "Reach ascension 10"),
]

class GameCore:
    def __init__(self):
        self.player = Player()
        self.upgrades: Dict[str, Upgrade] = self._init_upgrades()
        self.prestige_upgrades: Dict[str, PrestigeUpgrade] = create_prestige_upgrades()
        self.base_click_power = 1.0
        
        # Anti-autoclicker variables
        self.last_click_time = 0.0
        self.click_cooldown = 0.05 
        
        # Auto-clicker accumulator
        self.auto_click_accumulator = 0.0
        
        # Offline progress tracking
        self.offline_time_seconds = 0.0
        self.offline_lathams_gained = 0.0

    @property
    def ascension_threshold(self) -> float:
        return 750000 * (2.5 ** self.player.ascensions)

    def _init_upgrades(self) -> dict[str, Upgrade]:
        return {
            # --- Base tier (Ascension 0) ---
            "Beef Tallow Moisturiser": Upgrade("Beef Tallow Moisturiser", 15, 1.18, "click", 0.5, 0),
            "Sea Salt Spray": Upgrade("Sea Salt Spray", 150, 1.18, "idle", 1.0, 0),
            "Tear Maxxing": Upgrade("Tear Maxxing", 1500, 1.18, "idle", 12.0, 0),
            "Ice Roller": Upgrade("Ice Roller", 7500, 1.18, "idle", 50.0, 0),
            "Vitamin C Serum": Upgrade("Vitamin C Serum", 30000, 1.18, "idle", 200.0, 0),
            # --- Tier 2 (Ascension 1+) ---
            "Gua Sha": Upgrade("Gua Sha", 112500, 1.20, "idle", 500.0, 1),
            # --- Tier 3 (Ascension 2+) ---
            "Red Light Therapy": Upgrade("Red Light Therapy", 375000, 1.20, "idle", 1500.0, 2),
            # --- Tier 4 (Ascension 3+) ---
            "Cold Plunge": Upgrade("Cold Plunge", 1500000, 1.20, "idle", 5000.0, 3),
            # --- Tier 5 (Ascension 4+) ---
            "Mewing Coach": Upgrade("Mewing Coach", 7500000, 1.20, "idle", 20000.0, 4),
            # --- Tier 6 (Ascension 5+) ---
            "Jawline Sculptor": Upgrade("Jawline Sculptor", 37500000, 1.20, "idle", 100000.0, 5),
        }
    
    def get_visible_upgrades(self) -> dict[str, Upgrade]:
        """Return only upgrades the player has unlocked based on ascension count."""
        return {name: upg for name, upg in self.upgrades.items() 
                if upg.required_ascensions <= self.player.ascensions}
    
    def get_visible_prestige(self) -> dict[str, PrestigeUpgrade]:
        """Return only prestige upgrades the player has unlocked based on ascension count."""
        return {name: upg for name, upg in self.prestige_upgrades.items()
                if upg.required_ascensions <= self.player.ascensions}

    def get_prestige_bonus(self, effect_key: str) -> float:
        """Sum all purchased prestige bonuses for a given effect key."""
        return sum(p.effect_value for p in self.prestige_upgrades.values() 
                   if p.purchased and p.effect_key == effect_key)

    def has_prestige(self, effect_key: str) -> bool:
        """Check if any prestige upgrade with the given effect key is purchased."""
        return any(p.purchased and p.effect_key == effect_key 
                   for p in self.prestige_upgrades.values())

    @property
    def current_click_power(self) -> float:
        upgrade_bonus = sum(upg.total_bonus for upg in self.upgrades.values() if upg.effect_type == "click")
        click_mult = 1.0 + self.get_prestige_bonus("click_mult")
        return (self.base_click_power + upgrade_bonus) * self.player.ascensions_multiplier * click_mult
    
    @property
    def current_idle_power(self) -> float:
        upgrade_bonus = sum(upg.total_bonus for upg in self.upgrades.values() if upg.effect_type == "idle")
        idle_mult = 1.0 + self.get_prestige_bonus("idle_mult")
        return upgrade_bonus * self.player.ascensions_multiplier * idle_mult
    
    def click(self):
        """Attempt a click. Returns (power_earned, was_crit) if the click landed, else None."""
        current_time = time.time()
        if current_time - self.last_click_time >= self.click_cooldown:
            power = self.current_click_power

            # Critical click check (from prestige)
            crit_chance = self.get_prestige_bonus("crit_click")
            is_crit = crit_chance > 0 and random.random() < crit_chance
            if is_crit:
                power *= 5.0

            self.player.little_lathams += power
            self.player.total_lathams_earned += power
            self.last_click_time = current_time
            return (power, is_crit)
        return None
        
    def idle(self, delta_time: float):
        idle_earned = self.current_idle_power * delta_time
        self.player.little_lathams += idle_earned
        self.player.total_lathams_earned += idle_earned
        
        # Auto-clicker from prestige
        auto_rate = self.get_prestige_bonus("auto_click")
        if auto_rate > 0:
            self.auto_click_accumulator += delta_time * auto_rate
            while self.auto_click_accumulator >= 1.0:
                self.auto_click_accumulator -= 1.0
                power = self.current_click_power
                self.player.little_lathams += power
                self.player.total_lathams_earned += power
        
    def attempt_purchase(self, upgrade_name: str) -> bool:
        if upgrade_name in self.upgrades:
            upgrade = self.upgrades[upgrade_name]
            if upgrade.required_ascensions > self.player.ascensions:
                return False
            
            # Bulk buy check
            bulk_amount = int(self.get_prestige_bonus("bulk_buy")) if self.has_prestige("bulk_buy") else 1
            
            bought = False
            for _ in range(bulk_amount):
                if self.player.little_lathams >= upgrade.current_cost:
                    self.player.little_lathams -= upgrade.current_cost
                    upgrade.level_up()
                    bought = True
                else:
                    break
            return bought
        return False
    
    def attempt_prestige_purchase(self, upgrade_name: str) -> bool:
        """Attempt to purchase a prestige upgrade with AP."""
        if upgrade_name in self.prestige_upgrades:
            upgrade = self.prestige_upgrades[upgrade_name]
            if upgrade.can_purchase(self.player.ascension_points, self.player.ascensions):
                cost = upgrade.purchase()
                self.player.ascension_points -= cost
                return True
        return False
    
    def calculate_ap_reward(self) -> int:
        """Calculate how many AP the player earns for this ascension.
        Rewards more AP for overshooting the threshold."""
        threshold = self.ascension_threshold
        if self.player.little_lathams < threshold:
            return 0
        ratio = self.player.little_lathams / threshold
        return max(1, int(math.log2(ratio) + 1))
    
    def attempt_ascension(self) -> bool:
        if self.player.little_lathams >= self.ascension_threshold:
            # Award AP before resetting
            ap_earned = self.calculate_ap_reward()
            self.player.ascension_points += ap_earned
            
            # Apply starting bonus from prestige
            starting_bonus = self.get_prestige_bonus("starting_bonus")
            
            self.player.ascension_reset()
            self.player.little_lathams = starting_bonus  # Apply starting bonus
            
            for upgrade in self.upgrades.values():
                upgrade.reset()
            return True
        return False
    
    def get_unlocked_milestones(self) -> list:
        """Return a list of milestones the player has achieved."""
        return [(asc, name, desc) for asc, name, desc in MILESTONES 
                if self.player.ascensions >= asc]
    
    def get_next_milestone(self):
        """Return the next unachieved milestone, or None."""
        for asc, name, desc in MILESTONES:
            if self.player.ascensions < asc:
                return (asc, name, desc)
        return None

    def get_save_path(self):
        # Use Application Support on macOS or a sensible default elsewhere
        app_support = os.path.expanduser("~/Library/Application Support/LathamVerse")
        if not os.path.exists(app_support):
            try:
                os.makedirs(app_support)
            except OSError:
                app_support = os.path.abspath(".")
        return os.path.join(app_support, "savegame.json")

    def save_game(self, filename=None):
        if filename is None:
            filename = self.get_save_path()
        data = {
            "little_lathams": self.player.little_lathams,
            "ascensions": self.player.ascensions,
            "ascension_points": self.player.ascension_points,
            "total_lathams_earned": self.player.total_lathams_earned,
            "upgrades": {name: upg.level for name, upg in self.upgrades.items()},
            "prestige_purchased": [name for name, upg in self.prestige_upgrades.items() if upg.purchased],
            "last_save_time": time.time()
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_game(self, filename=None) -> bool:
        if filename is None:
            filename = self.get_save_path()
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                self.player.little_lathams = data.get("little_lathams", 0.0)
                self.player.ascensions = data.get("ascensions", 0)
                self.player.ascension_points = data.get("ascension_points", 0)
                self.player.total_lathams_earned = data.get("total_lathams_earned", 0.0)
                
                saved_upgrades = data.get("upgrades", {})
                for name, level in saved_upgrades.items():
                    if name in self.upgrades:
                        self.upgrades[name].level = level
                
                # Load prestige purchases
                prestige_purchased = data.get("prestige_purchased", [])
                for name in prestige_purchased:
                    if name in self.prestige_upgrades:
                        self.prestige_upgrades[name].purchased = True
                
                # Calculate offline progress
                saved_time = data.get("last_save_time", time.time())
                current_time = time.time()
                self.offline_time_seconds = min(max(0, current_time - saved_time), MAX_OFFLINE_SECONDS)
                
                # Apply offline multiplier from prestige
                offline_mult = 1.0
                offline_bonus = self.get_prestige_bonus("offline_mult")
                if offline_bonus > 0:
                    offline_mult = offline_bonus  # The value is already 2.0
                
                # Multiply time away by the newly loaded idle power
                self.offline_lathams_gained = self.offline_time_seconds * self.current_idle_power * offline_mult
                self.player.little_lathams += self.offline_lathams_gained
                self.player.total_lathams_earned += self.offline_lathams_gained
                
            return True # Successfully loaded
        return False # No save found