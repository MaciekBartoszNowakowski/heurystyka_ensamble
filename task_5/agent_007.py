import random
from enum import Enum

class ShipType(Enum):
    Attacker = 1
    Defender = 2
    Explorer = 3
    Conquerer = 4

class Agent:

    ship_types = {}

    def __init__(self, side: int):
        self.side = side
        self.enemy_base_x = None
        self.enemy_base_y = None
        self.home_base_x = None
        self.home_base_y = None
        self.map_x = 100
        self.map_y = 100
        self.step_nr = 0

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
        for ship in ships:
            if not ship[0] in self.ship_types.keys():
                self.ship_types[ship[0]] = ShipType.Attacker

        ships_actions = []
        type_to_method = {
            ShipType.Attacker: self.attacker,
            ShipType.Defender: self.defender,
            ShipType.Explorer: self.explorer,
            ShipType.Conquerer: self.conquerer,
        }

        for ship in ships:
            ships_actions.append(type_to_method[self.ship_types[ship[0]]](obs, ship))


        # if self.home_base_x is None or self.home_base_y is None:
        #     # Use the first allied ship's position as home base (if not already known)
        #     start_planet = obs['planets_occupation'][0]
        #     self.home_base_x = start_planet[0]
        #     self.home_base_y = start_planet[1]

        #     self.get_enemy_base()

        # self.get_next_step_direction()

        # # Send ships to the center of the map
        # for ship in obs['allied_ships']:
        #     ship_id, ship_x, ship_y, health, firing_cooldown, move_cooldown = ship


        #     # If the ship is not moving and not under cooldown
        #     if move_cooldown == 0:

        #         speed = 1  # Move 1 step at a time

        #         # Add ship action to move
        #         direction = self.get_next_step_direction(ship_x,ship_y)

        #         ships_actions.append([ship_id,0,direction,speed])

        # Decide whether to construct new ships (for simplicity, we just decide to construct 1 ship)
        # construction = 1

        return {
            "ships_actions": ships_actions,
            "construction": 20
        }


    def attacker(self, obs, ship):
        if self.home_base_x is None or self.home_base_y is None:
            # Use the first allied ship's position as home base (if not already known)
            start_planet = obs['planets_occupation'][0]
            self.home_base_x = start_planet[0]
            self.home_base_y = start_planet[1]

            self.get_enemy_base()

        # self.get_next_step_direction()

        ship_id, ship_x, ship_y, health, firing_cooldown, move_cooldown = ship
        direction = 0
        speed = 1
        # If the ship is not moving and not under cooldown
        if move_cooldown == 0:
            speed = 1 
            # Add ship action to move
            direction = self.get_next_step_direction(ship_x,ship_y)


        return [ship_id, 0, direction, speed]
    
    def defender(self, obs, ship):
        pass

    def explorer(self, obs, ship):
        pass

    def conquerer(self, obs, ship):
        pass
            


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

    def get_next_step_direction(self, pos_x, pos_y):
        if self.home_base_x < self.map_x/2:
            if abs(pos_x - self.home_base_x) < self.map_x/2 and abs(pos_y - self.home_base_y) < self.map_y/2 and pos_y != 0:
                return 3
            elif pos_y != self.enemy_base_y and pos_x != self.map_x -1:
                return 0
            elif pos_y != self.enemy_base_y:
                return 1
            elif pos_x != self.enemy_base_x:
                return 2
        if self.home_base_x > self.map_x/2:
            if abs(pos_x - self.home_base_x) < self.map_x/2 and abs(pos_y - self.home_base_y) < self.map_x/2 and pos_y != self.map_y - 1:
                return 1
            elif pos_y != self.enemy_base_y and pos_x != 1:
                return 2
            elif pos_y != self.enemy_base_y:
                return 3
            elif pos_x != self.enemy_base_x:
                return 0



    # Default to right if no movement is needed (though this shouldn't happen)

    def get_enemy_base(self):
        self.enemy_base_x = abs(self.home_base_x - self.map_x)
        self.enemy_base_y = abs(self.home_base_y - self.map_y)

    def load(self, abs_path: str):
        pass

    def eval(self):
        pass

    def to(self, device):
        pass
