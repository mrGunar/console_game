from ssl import OP_ENABLE_MIDDLEBOX_COMPAT
from map import Map
from player import Player, Direction
from monster import Monster
from coordinator import Coord
from bullet import Bullet
import itertools
from conf import Config
import random

import os

class Game:

    game = True

    def __init__(self, count_monsters=3) -> None:
        self.bussy_cells = list()
        self.map = Map()
        self.player = Player()
        self.monsters = [Monster.create_monster() for _ in range(count_monsters)]
        self.monsters = [x for x in self.monsters if x._is_alive]
        self.all_objects = [self.player] + self.monsters
        self.set_coords_to_obj(self.all_objects)

    def set_coords_to_obj(self, objs):
        for obj in objs:
            coords = Coord.generate_free_coord(self.bussy_cells)
            self.bussy_cells.append(coords)
            obj._x, obj._y = coords

    def get_available_cord(self, x, y):
        nei = [(1,1), (1,0), (-1,0), (-1,1), (-1,0), (-1,-1), (0, 1), (0, -1)]

        res = []
        for i, j in nei:
            dx = x - i
            dy = y - j
            if 0 < dx < Config.MAP_HEIGHT.value and 0 < dy < Config.MAP_WIDTH.value and \
            self.map.field[dx][dy] == Config.EMPTY_CELL.value:
                res.append((dx, dy))

        return random.choice(res) if res else (x, y)

    def set_coord(self, obj, x, y):
        obj._x = x
        obj._y = y

    def set_icon(self, x, y, icon):
        self.map.field[x][y] = icon

    def add_all_obj_to_map(self, objs):
        for obj in objs:
            self.set_icon(obj._x, obj._y, obj.icon)

    def monsters_step(self):

        random.shuffle(self.monsters)
        for x in self.monsters:
            old_cords = (x._x, x._y)
            self.bussy_cells.pop(self.bussy_cells.index(old_cords))

            new_cords = self.get_available_cord(*x.get_coords())
            self.bussy_cells.append(new_cords)
            
            self.set_coord(x, *new_cords)
            self.set_icon(*new_cords, x.icon)

    def user_step(self, user_choice):
        match user_choice:
            case "w":
                self.player.step(-1,0)
                self.player.last_direction = Direction.UP
            case "a":
                self.player.step(0,-1)
                self.player.last_direction = Direction.LEFT
            case "s":
                self.player.step(1,0)
                self.player.last_direction = Direction.DOWN
            case "d":
                self.player.step(0,1)
                self.player.last_direction = Direction.RIGHT
            case "z":
                bullet = Bullet(self.player._x, self.player._y)
                self.bullet_fly(bullet, self.player.last_direction)
            case _:
                print("Please repeat")
                return self.user_step(input("W A S D: "))
        self.set_icon(self.player._x, self.player._y, self.player.icon)


    def bullet_fly(self, bullet, last_direction):
        dx = 0
        dy = 0
        match last_direction:
            case Direction.UP:
                dx, dy = (1,0)
            case Direction.DOWN:
                dx, dy = (-1, 0)
            case Direction.RIGHT:
                dx, dy = (0,-1)
            case Direction.LEFT:
                dx, dy = (0,1)

        while 0 < bullet._x < Config.MAP_HEIGHT.value-1 and 0 < bullet._y < Config.MAP_WIDTH.value-1:
            bullet._x -= dx
            bullet._y -= dy
            kill_status = self.check_status_for_bullet_fly(bullet)
            self.set_icon(bullet._x, bullet._y, bullet.icon)
            if kill_status:
                break
            self.map.show_map()
            import time;time.sleep(0.05)
            os.system("cls")

    def check_status_for_bullet_fly(self, bullet):
        print(self.map.field[bullet._x][bullet._y])
        if self.map.field[bullet._x][bullet._y] == Config.MONSTER_ICON.value:
            monster = self.find_monster_with_coord(bullet._x, bullet._y)
            if monster:
                print("HEADSHOT")
                import time;time.sleep(1)
                monster.kill()
                return True
        return False

    def find_monster_with_coord(self, x, y):
        for m in self.monsters:
            if (x, y) == (m._x, m._y):
                return m

    def check_game_status(self):
        available_monster = True if [x for x in self.monsters if x._is_alive] else False
        self.check_status_player_near_monsters()

        return available_monster, self.player._is_alive

    def check_status_player_near_monsters(self):
        nei = [(1,1), (1,0), (-1,0), (-1,1), (-1,0), (-1,-1), (0, 1), (0, -1)]

        for i, j in nei:
            dx = self.player._x - i
            dy = self.player._y - j
            if 0 < dx < Config.MAP_HEIGHT.value and 0 < dy < Config.MAP_WIDTH.value and \
            self.map.field[dx][dy] == Config.MONSTER_ICON.value:
                self.player.is_alive = False

    def run(self):
        self.add_all_obj_to_map(self.all_objects)
        monster_status, player_status = True, True
        while Game.game:
            self.map.show_map()
            if not player_status:
                Game.game = False
                
                print("GAME OVER! YOU LOSE")
                input("Press any key...")
                break 
            print(f'{sum([1 for x in self.monsters if x._is_alive])} monsters remain')
            user_choice = input("Your step: w a s d: ")
            self.user_step(user_choice)
            monster_status, player_status = self.check_game_status()
            if not monster_status:
                Game.game = False
                print("GAME OVER")
                if player_status or not monster_status:
                    print("YOU WIN!")
                else:
                    print("YOU LOSE")
                input("Press any key...")
            self.monsters_step()
            self.add_all_obj_to_map(self.all_objects)

            self.map.draw_map(self.all_objects)
            # self.map.show_map()       

            
            os.system("cls")

        
