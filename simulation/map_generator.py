import heapq
import random
from itertools import tee, izip

from simulation.direction import ALL_DIRECTIONS
from simulation.location import Location
from simulation.world_map import WorldMap, Grid


def generate_map(height, width, obstacle_ratio):
    grid = Grid(width, height)

    # We designate one non-corner edge cell as empty, to ensure that the map can be expanded
    always_empty_edge_x, always_empty_edge_y = get_random_edge_index(height, width)

    for x, y in shuffled(_get_edge_coordinates(height, width)):
        if (x, y) != (always_empty_edge_x, always_empty_edge_y) and random.random() < obstacle_ratio:
            cell = grid.get_cell(Location(x, y))
            cell.habitable = False
            #   So long as all habitable neighbours can still reach each other, then the map cannot get bisected
            if not _all_habitable_neighbours_can_reach_each_other(cell, grid):
                cell.habitable = True

    return WorldMap(grid)


def _get_edge_coordinates(height, width):
    for x in xrange(width):
        for y in xrange(height):
            yield x, y


def shuffled(iterable):
    values = list(iterable)
    random.shuffle(values)
    return iter(values)


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def _all_habitable_neighbours_can_reach_each_other(cell, grid):
    neighbours = get_adjacent_habitable_cells(cell, grid)

    assert len(neighbours) >= 1
    return all(get_shortest_path_between(n1, n2, grid) is not None for n1, n2 in pairwise(neighbours))


def get_shortest_path_between(source_cell, destination_cell, grid):

    def manhattan_distance_to_destination_cell(this_branch):
        branch_tip_location = this_branch[-1].location
        abs(branch_tip_location.x - destination_cell.location.x) + abs(branch_tip_location.y - destination_cell.location.y) + len(this_branch)

    branches = PriorityQueue(key=manhattan_distance_to_destination_cell, init_items=[[source_cell]])
    visited_cells = set()

    while branches:
        branch = branches.pop()

        for cell in get_adjacent_habitable_cells(branch[-1], grid):
            if cell in visited_cells:
                continue

            visited_cells.add(cell)

            new_branch = branch + [cell]

            if cell == destination_cell:
                return new_branch

            branches.push(new_branch)

    return None


def get_random_edge_index(height, width, rng=random):
    assert height >= 2 and width >= 2

    num_row_cells = width - 2
    num_col_cells = height - 2
    num_edge_cells = 2*num_row_cells + 2*num_col_cells
    random_cell = rng.randint(0, num_edge_cells-1)

    if 0 <= random_cell < num_row_cells:
        # random non-corner cell on the first row
        return random_cell+1, 0
    elif num_row_cells <= random_cell < 2*num_row_cells:
        # random non-corner cell on the last row
        random_cell -= num_row_cells
        return random_cell + 1, height - 1

    random_cell -= 2*num_row_cells

    if 0 <= random_cell < num_col_cells:
        # random non-corner cell on the first column
        return 0, random_cell + 1
    elif num_col_cells <= random_cell < 2*num_col_cells:
        # random non-corner cell on the last column
        random_cell -= num_col_cells
        return width - 1, random_cell + 1

    raise ValueError('Should not be reachable')


def get_adjacent_habitable_cells(cell, grid):
    return [c for c in (grid.get_cell(cell.location + d) for d in ALL_DIRECTIONS) if c and c.habitable]


class PriorityQueue(object):
    def __init__(self, key, init_items=tuple()):
        self.key = key
        self.heap = [self._build_tuple(i) for i in init_items]
        heapq.heapify(self.heap)

    def _build_tuple(self, item):
        return self.key(item), item

    def push(self, item):
        to_push = self._build_tuple(item)
        heapq.heappush(self.heap, to_push)

    def pop(self):
        _, item = heapq.heappop(self.heap)
        return item

    def __len__(self):
        return len(self.heap)

