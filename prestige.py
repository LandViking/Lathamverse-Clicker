class PrestigeUpgrade:
    """A permanent upgrade purchased with Ascension Points (AP).
    These persist through ascensions and provide lasting bonuses."""
    
    def __init__(self, name: str, cost: int, description: str, 
                 effect_key: str, effect_value: float, required_ascensions: int):
        self.name = name
        self.cost = cost  # AP cost
        self.description = description
        self.effect_key = effect_key  # e.g. "click_mult", "idle_mult", "auto_click", etc.
        self.effect_value = effect_value
        self.required_ascensions = required_ascensions
        self.purchased = False

    def can_purchase(self, ap: int, ascensions: int) -> bool:
        """Check if the player can afford and has unlocked this upgrade."""
        return (not self.purchased 
                and ap >= self.cost 
                and ascensions >= self.required_ascensions)

    def purchase(self) -> int:
        """Mark as purchased and return the AP cost."""
        self.purchased = True
        return self.cost


def create_prestige_upgrades() -> dict[str, PrestigeUpgrade]:
    """Create and return all prestige upgrades in the game."""
    return {
        "Starting Bonus": PrestigeUpgrade(
            "Starting Bonus", 1,
            "Start each run with 50 Lathams",
            "starting_bonus", 50.0, 1
        ),
        "Click Mastery I": PrestigeUpgrade(
            "Click Mastery I", 1,
            "+50% base click power",
            "click_mult", 0.5, 1
        ),
        "Idle Mastery I": PrestigeUpgrade(
            "Idle Mastery I", 2,
            "+25% idle income",
            "idle_mult", 0.25, 1
        ),
        "Auto-Clicker": PrestigeUpgrade(
            "Auto-Clicker", 3,
            "1 automatic click per second",
            "auto_click", 1.0, 2
        ),
        "Click Mastery II": PrestigeUpgrade(
            "Click Mastery II", 3,
            "+100% base click power",
            "click_mult", 1.0, 2
        ),
        "Idle Mastery II": PrestigeUpgrade(
            "Idle Mastery II", 4,
            "+50% idle income",
            "idle_mult", 0.5, 3
        ),
        "Bulk Buy": PrestigeUpgrade(
            "Bulk Buy", 4,
            "Buy 10 upgrades at once",
            "bulk_buy", 10.0, 3
        ),
        "Critical Clicks": PrestigeUpgrade(
            "Critical Clicks", 5,
            "10% chance for 5x click damage",
            "crit_click", 0.10, 4
        ),
        "Offline Boost": PrestigeUpgrade(
            "Offline Boost", 5,
            "2x offline earnings",
            "offline_mult", 2.0, 4
        ),
        "Click Mastery III": PrestigeUpgrade(
            "Click Mastery III", 6,
            "+200% base click power",
            "click_mult", 2.0, 5
        ),
    }
