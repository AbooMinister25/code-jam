import time
from asyncio import Queue

from common.schemas import RoomChangeUpdate

if __name__ == "__main__":
    from game_objects import (
        ActionDict,
        BaseRoom,
        FleeDict,
        LeftLower,
        LeftTop,
        Mob,
        MovementDict,
        Player,
        RightLower,
        RightTop,
        RoomActionDict,
        RoughSide,
        SpidersDen,
        TopOfLeaf,
        Wall,
        raw_map,
    )
else:
    from game_components.game_objects import (
        ActionDict,
        BaseRoom,
        FleeDict,
        LeftLower,
        LeftTop,
        Mob,
        MovementDict,
        Player,
        RightLower,
        RightTop,
        RoomActionDict,
        RoughSide,
        SpidersDen,
        TopOfLeaf,
        Wall,
        raw_map,
    )


class Game:
    players: dict[int, Player]
    mobs: dict[int, Mob]
    rooms: dict[int, BaseRoom]
    start_time: int

    def __init__(self):
        self.out_queue: Queue[
            ActionDict
            | MovementDict
            | RoomActionDict
            | FleeDict
            | RoomChangeUpdate
            | int
        ] = Queue()
        self.players = {}
        self.mobs = {}
        self.rooms = {}
        self.build_map()
        self.start_time = round(time.time() * 1000)

    def get_room_at(self, x: int, y: int) -> BaseRoom | None:
        temp = None
        for room in self.rooms.values():
            if room.get_map_location() == (x, y):
                temp = room
                break
        return temp

    def get_room(self, _uid: int) -> BaseRoom | None:
        return self.rooms.get(_uid)

    def get_player(self, _uid: int) -> Player | None:
        return self.players.get(_uid)

    def get_mob(self, _uid: int) -> Mob | None:
        return self.mobs.get(_uid)

    def build_map(self) -> None:
        largest_x = 0
        largest_y = 0
        for room_data in raw_map:
            temp = None
            if room_data["type"] == "rs":
                temp = RoughSide(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "wall":
                temp = Wall(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "ll":
                temp = LeftLower(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "rl":
                temp = RightLower(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "rt":
                temp = RightTop(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "lt":
                temp = LeftTop(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "sd":
                temp = SpidersDen(_display_x=room_data["x"], _display_y=room_data["y"])
            elif room_data["type"] == "tol":
                temp = TopOfLeaf(_display_x=room_data["x"], _display_y=room_data["y"])
            if room_data["x"] > largest_x:
                largest_x = room_data["x"]
            if room_data["y"] > largest_y:
                largest_y = room_data["y"]
            assert temp, f"unknown room type {room_data['type']}"
            self.rooms[temp.uid] = temp

        for y in range(largest_y + 1):
            for x in range(largest_x + 1):
                current_room = None
                for room in self.rooms.values():
                    if room.get_map_location() == (x, y):
                        current_room = room
                        break
                if current_room is not None:
                    directions: dict[str, None | BaseRoom] = {
                        "north": None,
                        "east": None,
                        "south": None,
                        "west": None,
                    }

                    for room in self.rooms.values():
                        if room.get_map_location() == (
                            current_room.display_x,
                            current_room.display_y - 1,
                        ):
                            directions["north"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x,
                            current_room.display_y + 1,
                        ):
                            directions["south"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x - 1,
                            current_room.display_y,
                        ):
                            directions["west"] = room
                            continue
                        if room.get_map_location() == (
                            current_room.display_x + 1,
                            current_room.display_y,
                        ):
                            directions["east"] = room
                            continue
                    current_room.set_links(directions)

    def add_player(self, player: Player, target_x: int, target_y: int) -> bool:
        room = self.get_room_at(target_x, target_y)
        assert room

        if not room.can_entity_step:
            return False

        if player.uid not in self.players:
            self.players[player.uid] = player

        room.add_player(player)
        return True

    def move_player(self, player: Player, direction: str) -> bool:
        if direction not in ("north", "east", "west", "south"):
            return False

        player_moved = False

        from_room = player.in_room
        to_go = from_room.get_links()[direction]

        if to_go is not None and to_go.can_entity_step:
            from_room.remove_player(player)
            to_go.add_player(player)
            player_moved = True

        return player_moved

    def add_mob(self, mob: Mob, target_x: int, target_y: int) -> bool:
        room = self.get_room_at(target_x, target_y)
        assert room
        assert room.can_entity_step

        self.mobs[mob.uid] = mob
        room.add_mob(mob)
        return True

    async def update(self):
        for mob_uid in self.mobs:
            self.mobs[mob_uid].update()

        for player_uid in self.players:
            action_performed = self.players[player_uid].update()

            match action_performed:
                case list():
                    if len(action_performed) == 0:
                        await self.out_queue.put({"no_target": player_uid})
                    for action in action_performed:
                        await self.out_queue.put(action)
                case dict():
                    await self.out_queue.put(action_performed)
                case _:
                    await self.out_queue.put({"no_action": action_performed})

        for room_uid in self.rooms:
            for event in self.rooms[room_uid].events:
                await self.out_queue.put(event)
            self.rooms[
                room_uid
            ].events = (
                []
            )  # If an event was missed for whatever reason... to bad... it's a feature!


if __name__ == "__main__":
    # required
    g = Game()

    # adding a player to a specific room
    A = Player("xyf", ["bite", "spit"], g)
    temp = g.get_room_at(1, 1)
    assert temp, "no room at (1, 1)"
    temp.add_player(A)

    # adding a mob
    a = Mob("anta", ["bite"])
    temp = g.get_room_at(1, 1)
    assert temp, "no room at (1, 1)"
    temp.add_mob(a)

    # adding a mob to a map location
    b = Mob("antb", ["bite"])
    g.add_mob(b, 1, 1)

    """
    # testing entity combat
    print(temp)
    result = A.commit_action("bite", a)
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")

    print(temp)
    result = A.commit_action("spit")
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    """
    """
    # testing player updating.
    A.add_command_to_queue("bite", a)
    result = A.update()
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    A.add_command_to_queue("spit")
    result = A.update()
    for event in result:
        print("----")
        for k, v in event.items():
            print(f"\t{k}: {v}")
    print(temp)
    """

    # Test movements.
    print("~~~~~~~~~~~")
    A5 = Player("A5Rocks", ["bite", "spit"], g)
    g.add_player(A5, 1, 1)
    print(g.get_room_at(1, 1).get_players())
    A5.add_command_to_queue("east", None)
    g.update()
    print(A5.command_queue)
    print(g.get_room_at(1, 1).get_players())
