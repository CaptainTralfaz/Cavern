from queue import Queue
from random import randint, choice, shuffle

import pygame

life_directions = {(-1, -1), (-1, 0), (-1, 1), (0, 1),
                   (1, 1), (1, 0), (1, -1), (0, -1)}

ortho_directions = {(1, 0), (0, 1), (-1, 0), (0, -1)}


class LifeMap:
    def __init__(self, map_width, map_height):
        """
        Creates a new map (list of lists) and initializes it to all random, except for a filled border
        :param map_width: width of map
        :param map_height: height of map
        """
        self.width = map_width
        self.height = map_height
        self.alive = [[True for y in range(0, self.height)] for x in range(0, self.width)]
    
    def make_random(self):
        for x in range(1, self.width - 2):
            for y in range(1, self.height - 2):
                if randint(0, 1):
                    self.alive[x][y] = False


def carve_cavern(grid, caverns):
    """
    Sets each point in a list of cavern coordinates as False
    Chooses a random coordinate in each separate cavern set,
    and then connects those points in a random-walk algorithm,
    setting to false as it progresses
    :param grid: current 2d boolean array
    :param caverns: list of list of tuples representing unconnected caverns
    :return: modified grid, and list of corridor coordinates
    TODO should probably move random walk to another method
    """
    connections_start = []
    connections_end = []
    for tile_set in caverns:
        for tile in tile_set:
            (x, y) = tile
            grid.alive[x][y] = False
        connections_start.append(choice(tile_set))
        connections_end.append(choice(tile_set))
    corridors = []
    for i in range(-1, len(connections_start) - 1):
        (x, y) = connections_start[i]
        (x2, y2) = connections_end[i + 1]
        while (x, y) != (x2, y2):
            if x == x2:  # move y
                if y < y2:
                    y += 1
                else:
                    y -= 1
            elif y == y2:  # move x
                if x < x2:
                    x += 1
                else:
                    x -= 1
            else:
                if randint(0, 1):  # randomly pick x or y
                    if y < y2:
                        y += 1
                    else:
                        y -= 1
                else:
                    if x < x2:
                        x += 1
                    else:
                        x -= 1
            grid.alive[x][y] = False
            corridors.append((x, y))
    return grid, corridors


def cleanup(grid, min_cavern_size):
    """
    Create a map without the small caverns, with all valid caverns connected
    :param grid: current 2d boolean array
    :param min_cavern_size: int minimum size of unconnected
    :return: modified copy of grid, list of corridors
    """
    new_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    # copy grid
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y]:
                new_grid.alive[x][y] = False
    
    # get a map without the small caverns, with all valid caverns connected
    new_grid, corridors = fill_small_caverns(grid=new_grid, min_cavern_size=min_cavern_size)
    
    return new_grid, corridors


def fill_small_caverns(grid, min_cavern_size):
    """
    Finds the coordinates of all enclosed caverns, sends only valid caverns to be carved
    :param grid: current LifeMap object
    :param min_cavern_size: int minimum cavern size to keep
    :return: current lifeMap object
    """
    cavern_tiles = []  # holds set of all coordinates in largest caverns found so far
    explored = []
    new_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    for x in range(new_grid.width):
        for y in range(new_grid.height):
            if (x, y) not in cavern_tiles and (x, y) not in explored and not grid.alive[x][y]:
                # get all tiles in this cave system
                new_cave_tiles = explore_cavern_iterative_ortho(grid, x, y)
                # compare size of new cave tiles to current tile
                explored.extend(new_cave_tiles)
                if len(new_cave_tiles) >= min_cavern_size:
                    cavern_tiles.append(new_cave_tiles)
    new_map, corridors = carve_cavern(grid=new_grid, caverns=cavern_tiles)
    return new_map, corridors


def get_neighbor_count(grid, x, y, state):
    """
    Convenience function: Returns a count of tuple x y coordinates matching a desired state - diagonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    return len(get_neighbors_list(grid=grid, x=x, y=y, state=state))


def get_neighbor_count_ortho(grid, x, y, state):
    """
    Convenience function: Returns a count of tuple x y coordinates matching a desired state - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    return len(get_neighbors_list_ortho(grid=grid, x=x, y=y, state=state))


def get_neighbors_list(grid, x, y, state):
    """
    Returns a list of tuple x y coordinates matching a desired state - diagonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    neighbors = []
    for direction in life_directions:
        dx, dy = direction
        if grid.alive[dx + x][dy + y] == state:
            neighbors.append((dx + x, dy + y))
    return neighbors


def get_neighbors_list_ortho(grid, x, y, state):
    """
    Returns a list of tuple x y coordinates matching a desired state - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :param state: desired boolean state to match
    :return: list of tuple x y coordinates
    """
    neighbors = []
    for direction in ortho_directions:
        (dx, dy) = direction
        if grid.alive[dx + x][dy + y] == state:
            neighbors.append((dx + x, dy + y))
    return neighbors


def explore_cavern_iterative(grid, x, y):
    """
    Iteratively explores a cavern, returns a list of all coordinates in that cavern - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :return: list of tuple x y coordinates
    """
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_neighbors_list(grid, x, y, state=False):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited


def explore_cavern_iterative_ortho(grid, x, y):
    """
    Iteratively explores a cavern, returns a list of all coordinates in that cavern - orthogonal version
    :param grid: LifeMap object
    :param x: x coordinate
    :param y: y coordinate
    :return: list of tuple x y coordinates
    """
    frontier = Queue()
    frontier.put((x, y))
    visited = [(x, y)]
    
    while not frontier.empty():
        current = frontier.get()
        x, y = current
        for neighbor in get_neighbors_list_ortho(grid, x, y, state=False):
            if neighbor not in visited:
                frontier.put(neighbor)
                visited.append(neighbor)
    return visited


def cycle(grid, survive_min, survive_max, resurrect_min, resurrect_max):
    """
    Heart of the Conway's Game Of Life algorithm for our purposes
    (credit to https://gridbugs.org/cellular-automata-cave-generation/)
    :param grid: list of lists of booleans denoting map
    :param survive_min: minimum number of neighbors needed to keep state
    :param survive_max: maximum number of neighbors allowed to keep state
    :param resurrect_min: minimum number of neighbors needed to change state
    :param resurrect_max: maximum number of neighbors allowed to change state
    :return: current lifeMap object after iteration
    """
    next_grid = LifeMap(map_width=grid.width, map_height=grid.height)
    for x in range(1, grid.width - 2):
        for y in range(1, grid.height - 2):
            neighbor_count = get_neighbor_count(grid=grid, x=x, y=y, state=True)
            if grid.alive[x][y]:
                if survive_min <= neighbor_count <= survive_max:
                    next_grid.alive[x][y] = True
                else:
                    next_grid.alive[x][y] = False
            else:
                if resurrect_min <= neighbor_count <= resurrect_max:
                    next_grid.alive[x][y] = True
                else:
                    next_grid.alive[x][y] = False
    return next_grid


def make_zones(grid, desired_seeds, zone_seed_min_distance):
    """
    Creates zones to be used for monster / treasure placement (instead of rooms)
    :param grid: LifeMap object
    :param desired_seeds: number of desired zones (more of a guideline)
    :param zone_seed_min_distance: int minimum orthogonal distance between seeds
    :return: list of lists of tuple int x y coordinates
    TODO this should probably be split into other methods
    """
    # copy map
    taken_grid = LifeMap(grid.width, grid.height)
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y]:
                taken_grid.alive[x][y] = False
    
    # prepare a list of seed candidates that have no "live" neighbors on the grid, and are not next to a seed
    candidates = []
    for x in range(1, taken_grid.width - 2):
        for y in range(1, taken_grid.height - 2):
            if not taken_grid.alive[x][y] and get_neighbor_count_ortho(taken_grid, x, y, False) == 4:
                candidates.append((x, y))
                taken_grid.alive[x][y] = True
    
    # determine seeds to grow zones
    seeds = []
    if len(candidates) < desired_seeds:
        seeds = candidates
    else:
        # create initial seed
        shuffle(candidates)
        seed = (candidates[0])
        seeds.append(seed)
        candidates.remove(seed)
        candidates = remove_closest_candidates(seed, candidates, zone_seed_min_distance)
        # create seeds until there are no valid candidates, or there are enough seeds
        while candidates and len(seeds) < desired_seeds:
            furthest = furthest_candidate_from_all_seeds(seeds=seeds, candidates=candidates)
            seeds.append(furthest)
            candidates.remove(furthest)
            candidates = remove_closest_candidates(seed=furthest, candidates=candidates,
                                                   zone_seed_min_distance=zone_seed_min_distance)
    
    # convert lifeMap object into a list of valid coordinates
    grid_list = []
    for x in range(grid.width):
        for y in range(grid.height):
            if not grid.alive[x][y]:
                grid_list.append((x, y))
    
    # change list of seed tuples into a list of lists
    zones = []
    for seed in seeds:
        zones.append([seed])
    
    # grow seeds into zones, until there are no more valid coordinates to choose from
    while grid_list:
        zones, grid_list = grow_zones(zones=zones, grid_list=grid_list, grid=grid)
    
    return zones


def grow_zones(zones, grid_list, grid):
    """
    Iterate through zones tile by tile, appending each tile's valid neighbors to it's zone
    :param zones: list of lists of tuple int x y coordinates
    :param grid_list: LifeMap object (array of array of booleans)
    :param grid:
    :return:
    """
    zone_list = []
    for zone in zones:
        new_zone = []
        for (x, y) in zone:
            new_zone.append((x, y))
            neighbors = get_neighbors_list_ortho(grid=grid, x=x, y=y, state=False)
            for neighbor in neighbors:
                if neighbor in grid_list:
                    new_zone.append(neighbor)
                    grid_list.remove(neighbor)
        zone_list.append(new_zone)
    return zone_list, grid_list


def remove_closest_candidates(seed, candidates, zone_seed_min_distance):
    """
    Removes all candidates with orthogonal distance smaller than the given min distance
    :param seed: tuple x y int coordinates
    :param candidates: list of tuple x y int coordinates that can be removed
    :param zone_seed_min_distance: minimum distance coordinates must be from seed
    :return: list of tuple x y int valid candidates
    """
    good_list = []
    (x1, y1) = seed
    for candidate in candidates:
        (x2, y2) = candidate
        good_candidate = True
        if distance_to(x1, y1, x2, y2) < zone_seed_min_distance:
            good_candidate = False
        if good_candidate:
            good_list.append(candidate)
    return good_list


def furthest_candidate_from_all_seeds(seeds, candidates):
    """
    Returns the candidate coordinate that is the farthest in distance from all seeds
    :param seeds: list of int x y coordinate tuples
    :param candidates: list of int x y coordinate tuples
    :return: tuple x y int coordinates
    """
    furthest_dist = 0
    furthest_candidate = (None, None)
    for (x1, y1) in candidates:
        current_dist = 0
        for (x2, y2) in seeds:
            current_dist += distance_to(x1, y1, x2, y2)
            if current_dist > furthest_dist:
                furthest_dist = current_dist
                furthest_candidate = (x1, y1)
    return furthest_candidate


def distance_to(x1, y1, x2, y2):
    """
    Sum the difference between two points
    :param x1: point 1 x coord
    :param y1: point 1 y coord
    :param x2: point 2 x coord
    :param y2: point 2 y coord
    :return: int orthogonal distance
    """
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return dx + dy


def draw_display(display, corridors, block_size, zones=None):
    block = pygame.Surface((block_size, block_size))
    small_block = pygame.Surface((block_size // 2, block_size // 2))
    small_block.fill((255, 255, 255))
    
    display.fill((0, 0, 0))
    for zone in zones:
        color = (randint(50, 255), randint(50, 255), randint(50, 255))
        for (x, y) in zone:
            block.fill(color)
            display.blit(block, (x * block_size, y * block_size))
            if (x, y) in corridors:
                small_block.fill((255, 255, 255))
                display.blit(small_block, (x * block_size + block_size // 4, y * block_size + block_size // 4))


def main():
    # map size (currently set for python roguelike tutorial at panel stage
    map_width = 80
    map_height = 43
    
    # pygame display info
    block_size = 12
    pygame.init()
    display = pygame.display.set_mode((map_width * block_size, map_height * block_size))
    pygame.display.set_caption('Cavern Life')
    display.fill((255, 255, 255))
    
    # Conway's Game Of Life variables
    # 3 6 5 6 3 - good choice
    # 3 6 5 7 3 - another good choice
    survive_min = 3
    survive_max = 6
    resurrect_min = 5
    resurrect_max = 6
    iterations = 5

    # zone variables
    zone_seed_min_distance = 12
    num_zone_seeds = map_width * map_height // 100
    min_cavern_size = 15

    game_quit = False
    
    while not game_quit:
        
        stop = True
        
        # create random LifeMap object
        life_map = LifeMap(map_width=map_width, map_height=map_height)
        life_map.make_random()
        
        # cycle LifeMap object a desired number of times
        for i in range(iterations):
            life_map = cycle(grid=life_map, survive_min=survive_min, survive_max=survive_max,
                             resurrect_min=resurrect_min, resurrect_max=resurrect_max)
            
        # clean up LifeMap object, connecting areas that are large enough
        life_map, corridors = cleanup(grid=life_map, min_cavern_size=min_cavern_size)
        
        # create zones (rooms) in map for monster/tresure placement
        zones = make_zones(grid=life_map, desired_seeds=num_zone_seeds, zone_seed_min_distance=zone_seed_min_distance)
        
        # display result
        draw_display(display=display, corridors=corridors, block_size=block_size, zones=zones)
        pygame.display.flip()
        
        # pygame control system - any key will create a new map to display, ESC to quit
        while stop and not game_quit:
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                    stop = False
                
                elif event.type == pygame.QUIT:
                    game_quit = True
                else:
                    continue


if __name__ == '__main__':
    main()
