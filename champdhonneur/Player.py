import Action as a

class Player:
    def __init__(self, name, unit, city):
        self._name = name
        self.unit = unit
        self.city = city

        self._last_action = None
        self.units_side = 12 # 12
        self.units_bag = 5 # 5
        self.units_hand = 3 # 3
        self.units_used = 0

    def copy(self):
        new_player = Player(self._name, self.unit, self.city)
        new_player._last_action = self._last_action
        new_player.units_side = self.units_side
        new_player.units_bag = self.units_bag
        new_player.units_hand = self.units_hand
        new_player.units_used = self.units_used
        return new_player