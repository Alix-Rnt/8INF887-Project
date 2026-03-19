class Tile:
    _W = "w" # white unit
    _B = "b" # black unit
    _C = "C" # unclaimed city
    _C_W = "W" # white city
    _C_B = "B" # white city
    _E, = ' ' # empty unit or city
    _O = "/" # out

    def __init__(self, is_city):
        self.unit = self._E
        self.unit_amount = 0
        self.is_city = is_city
        if is_city:
            self.city = self._C
        else:
            self.city = self._E

    def copy(self):
        new_tile = Tile(self.is_city)
        new_tile.unit_amount = self.unit_amount
        new_tile.city = self.city
        return new_tile