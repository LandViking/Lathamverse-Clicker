class gamecore:
    def __init__(self):
        self.player = player()
        self.upgrades = dict[str, upgrade] = self._init_upgrades()