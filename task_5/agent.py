import random
from enum import Enum


class ShipType(Enum):
    Attacker = 0
    Defender = 1
    Explorer = 2
    Conquerer = 3
    Horde = 4


class Agent:
    ship_types = {}

    def __init__(self, side: int):
        self.side = side
        self.enemy_base_x = 91
        self.enemy_base_y = 91
        self.home_base_x = 9
        self.home_base_y = 9
        self.map_x = 100
        self.map_y = 100
        if side == 1:
            self.enemy_base_x, self.enemy_base_y, self.home_base_x, self.home_base_y = self.home_base_x, self.home_base_y, self.enemy_base_x, self.enemy_base_y
        self.ship_state_map = {}

        self.side = side
        self.timeouts = {}
        self.upper_start = False
        self.turn = 0
        self.ship_number = 0

        self.new_planet_discovered = None

    def count_type(self, obs:dict):
        types = [0 for _ in range(len(ShipType))] # Attacker, Defender, Explorer, Conquerer
        if obs is None or obs['allied_ships'] is None:
            return types
        
        for ship in obs['allied_ships']:
            ship_id = ship[0]
            if ship_id in self.ship_types.keys():
                types[self.ship_types[ship_id].value] += 1

        return types


    def select_type(self, obs:dict):
        sequence = [ShipType.Attacker, ShipType.Attacker, ShipType.Defender, ShipType.Explorer]
        types = self.count_type(obs)

        if self.turn >= 1750:
            return ShipType.Horde

        if self.ship_number < len(sequence):
            if types[ShipType.Defender.value] < 1 and self.ship_number > 2:
                return ShipType.Defender
            return sequence[self.ship_number]

        random_value = random.randint(0, 9)

        if types[ShipType.Defender.value] < 2:
            return ShipType.Defender
        elif random_value < 3:
            return ShipType.Attacker
        else:
            return ShipType.Explorer

    def get_action(self, obs: dict) -> dict:
        """
        Main function, which gets called during step() of the environment.

        :param obs:
        allied_ships: an array of all currently available ships for the player. The ships are represented as a list:
                (ship id, position x, y, current health points, firing_cooldown, move_cooldown)
                - ship id: int [0, 1000]
                - position x: int [0, 100]
                - position y: int [0, 100]
                - health points: int [1, 100]
                - firing_cooldown: int [0, 10]
                - move_cooldown: int [0, 3]
        :return:
        """

        # add new ships to types
        ships = obs['allied_ships']

        print("PRINT TYPES:", self.count_type(obs))

        allied_ships = obs['allied_ships']

        if self.turn == 0:
            if allied_ships[0][1] < 50:
                self.upper_start = True

        self.turn += 1

        if self.new_planet_discovered == None:
            for i, planet in enumerate(obs['planets_occupation']):
                if planet[2] == -1:
                    self.new_planet_discovered = i

        for ship in ships:
            new_type = self.select_type(obs)
            if not ship[0] in self.ship_types.keys():
                self.ship_types[ship[0]] = new_type
                self.ship_number += 1
            
            if new_type == ShipType.Attacker:
                for ship_id, ship_type in self.ship_types.items():
                    if self.ship_types[ship_id] == ShipType.Defender:
                        self.ship_types[ship_id] = ShipType.Attacker
                        break

            if self.turn >= 1750:
                for ship_id, ship_type in self.ship_types.items():
                    if ship_type == ShipType.Explorer:
                        self.ship_types[ship_id] = ShipType.Horde


        ships_actions = []
        type_to_method = {
            ShipType.Attacker: self.attacker,
            ShipType.Defender: self.defender,
            ShipType.Explorer: self.explorer,
            ShipType.Conquerer: self.conquerer,
            ShipType.Horde: self.horde,
        }

        for ship in ships:
            ships_actions.append(type_to_method[self.ship_types[ship[0]]](obs, ship))

        self.new_planet_discovered = None

        return {
            "ships_actions": ships_actions,
            "construction": 20
        }

    def attacker(self, obs, ship):
        ship_id, ship_x, ship_y, health, firing_cooldown, move_cooldown = ship

        direction = 0
        speed = 3

        direction = self.get_next_step_direction(ship_id, ship_x, ship_y)

        return [ship_id, 0, direction, speed]

    def defender(self, obs, ship):
        id, my_x, my_y, _, _, _ = ship
        return [id, 1, 1]

    def explorer(self, obs, ship):
        ship_id, _, _, _, _, _ = ship
        if self.new_planet_discovered != None:
            if self.get_distance(ship[1], ship[2], obs['planets_occupation'][self.new_planet_discovered][1],
                                 obs['planets_occupation'][self.new_planet_discovered][0]) <= 15:
                return [ship_id, 0, self.calculate_direction(ship[1], ship[2],
                                                             obs['planets_occupation'][self.new_planet_discovered][1],
                                                             obs['planets_occupation'][self.new_planet_discovered][0]),
                        3]

        if self.upper_start:
            possible = [0, 1, 1, 1, 3, 3]
        else:
            possible = [2, 1, 1, 3, 3, 3]

        if ship_id in self.timeouts:
            time, side = self.timeouts[ship_id]
            if time != 0:
                time -= 1
                self.timeouts[ship_id] = [time, side]
            else:
                self.timeouts[ship_id] = [random.randint(15, 23), possible[random.randint(0, 5)]]
        else:
            self.timeouts[ship_id] = [random.randint(15, 23), possible[random.randint(0, 5)]]

        time, side = self.timeouts[ship_id]
        return [ship_id, 0, side, 3]

    def conquerer(self, obs, ship):
        pass

    def horde(self,obs,ship):
        id, my_x, my_y, _, _, _ = ship

        return [id, 0, self.calculate_direction(my_x, my_y, self.enemy_base_x, self.enemy_base_y), 3]


    def calculate_direction(self, ship_x: int, ship_y: int, target_x: int, target_y: int) -> int:
        """
        Given the current position of the ship and the target position, calculate the direction
        to move, encouraging the ship to move diagonally by prioritizing the axis with the greater distance.

        Directions are defined as:
            0 - right
            1 - down
            2 - left
            3 - up
        """
        # Calculate horizontal and vertical difference
        dx = target_x - ship_x
        dy = target_y - ship_y

        # Prioritize movement along the greater absolute distance
        if abs(dx) >= abs(dy):
            # Move horizontally (right or left)
            return 0 if dx > 0 else 2
        else:
            # Move vertically (down or up)
            return 1 if dy > 0 else 3

    def get_next_step_direction(self, ship_id, pos_x, pos_y):
        padding = 2

        self.ship_state_map.setdefault(ship_id, 0)
        if self.get_distance(pos_x, pos_y, self.enemy_base_x, self.enemy_base_y) <= 15:
            return self.calculate_direction(pos_x, pos_y, self.enemy_base_x, self.enemy_base_y)
        if self.ship_state_map[ship_id] == 0:
            if pos_x > pos_y:
                if pos_x > self.map_y - pos_y:
                    if pos_x == self.map_x - 1 - padding:
                        self.ship_state_map[ship_id] = 3
                    else:
                        return 0
                else:
                    if pos_y == 0 + padding:
                        self.ship_state_map[ship_id] = 1
                    else:
                        return 3
            else:
                if pos_x > self.map_y - pos_y:
                    if pos_y == self.map_y - 1 - padding:
                        self.ship_state_map[ship_id] = 4
                    else:
                        return 1
                else:
                    if pos_x == 0 + padding:
                        self.ship_state_map[ship_id] = 2
                    else:
                        return 2

        elif self.ship_state_map[ship_id] == 1:
            if self.side == 0:
                if pos_x == self.map_x - 1 - padding:
                    self.ship_state_map[ship_id] = 3
                else:
                    return 0
            else:
                if pos_x == 0 + padding:
                    self.ship_state_map[ship_id] = 5
                else:
                    return 2

        elif self.ship_state_map[ship_id] == 2:
            if self.side == 0:
                if pos_y == self.map_y - 1 - padding:
                    self.ship_state_map[ship_id] = 4
                else:
                    return 1
            else:
                if pos_y == 0 + padding:
                    self.ship_state_map[ship_id] = 5
                else:
                    return 3

        elif self.ship_state_map[ship_id] == 3:
            if self.side == 0:
                if pos_y == self.map_y - 1 - padding:
                    self.ship_state_map[ship_id] = 5
                else:
                    return 1
            else:
                if pos_y == 0 + padding:
                    self.ship_state_map[ship_id] = 1
                    return self.get_next_step_direction(ship_id, pos_x, pos_y)
                else:
                    return 2

        elif self.ship_state_map[ship_id] == 4:
            if self.side == 0:
                if pos_x == self.map_x - 1 - padding:
                    self.ship_state_map[ship_id] = 5
                else:
                    return 0
            else:
                if pos_x == 0 + padding:
                    self.ship_state_map[ship_id] = 2

                    return self.get_next_step_direction(ship_id, pos_x, pos_y)
                else:
                    return 2

        elif self.ship_state_map[ship_id] == 5:
            return self.calculate_direction(pos_x, pos_y, self.enemy_base_x, self.enemy_base_y)

        return self.calculate_direction(pos_x, pos_y, self.enemy_base_x, self.enemy_base_y)  # Fallback return

    # Default to right if no movement is needed (though this shouldn't happen)

    def get_enemy_base(self):
        self.enemy_base_x = abs(self.home_base_x - self.map_x)
        self.enemy_base_y = abs(self.home_base_y - self.map_y)

    def get_distance(self, x_1, y_1, x_2, y_2):
        return (abs(x_1 - x_2) ** 2 + abs(y_1 - y_2) ** 2) ** (1 / 2)

    def load(self, abs_path: str):
        pass

    def eval(self):
        pass

    def to(self, device):
        pass