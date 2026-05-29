class Player:
    def __init__(self):
    # This class represents the player in the game, tracking their resources and progress.
        self.little_lathams: float = 0.0
        self.ascensions: int = 0
        
    @property
    # The ascensions_multiplier property calculates the multiplier for little lathams based on the number of ascensions.
    def ascensions_multiplier(self) -> float:
        return 1.0 + (self.ascensions * 0.5)    
    
    def ascension_reset(self):
    # This method resets the player's progress when they perform an ascension, granting them a boost in little lathams per second.
        self.ascensions += 1
        self.little_lathams = 0.0