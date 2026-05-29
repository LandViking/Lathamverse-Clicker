class Upgrade:
    def __init__(self, name: str, base_cost: float, scaling: float, effect_type: str, base_power: float):
        self.name = name
        self.base_cost = base_cost
        self.scaling = scaling
        self.effect_type = effect_type #click or idle
        self.base_power = base_power
        self.level = 0
        
    @property
    def current_cost(self) -> float:
        return self.base_cost * (self.scaling ** self.level)

    @property
    def total_bonus(self) -> float:
        return self.base_power * self.level
    
    def level_up(self):
        self.level += 1
        
    def reset(self):
        self.level = 0
