from collections import defaultdict, deque

type VennSetName = str | tuple[str, ...]
type GraphSet = dict[str, 'VennSet']

from VennSet import VennSet
from VennElem import VennElem
from VennGraph import VennGraph

ALLOWED_VENN_GRAPH_SIZES = [2, 3, 8]



class Domino:
    def __init__(self, val1, val2):
        self.vals = [val1, val2]
        self.id = hash(tuple(self.vals))

    def has(self, val: int):
        return val in self.vals

    def __repr__(self) -> str:
        return f'{self.vals}'


def start_board():
    domino_map = defaultdict(list)
    all_dominoes = []
    for i in range(7):
        for j in range(i, 7):
            domino = Domino(i, j)
            domino_map[i].append(domino)
            all_dominoes.append(domino)
            if i != j:
                domino_map[j].append(domino)
    return domino_map, all_dominoes


# Setting up Dominos. They're just arrays of size 2 representing the numbers
# on each end of the tile.
domino_map, all_dominoes = start_board()

# Setting up the venn diagram representation of players/dominos they
# can pick from.
p1 = "A"
p2 = "B"
p3 = "C"
three_set_venn_diagram = VennGraph(p1, p2, p3)
three_set_venn_diagram.add_to_set(all_dominoes, p1, p2, p3)
three_set_venn_diagram.put_in_set([all_dominoes[1]], p1)
three_set_venn_diagram.put_in_set([all_dominoes[5]], p1, p2)
three_set_venn_diagram.remove_from_graph([all_dominoes[0]])


class SubPartition:
    """ IDK - a partition is a way to build the whole set by chunks? In this case
    we care about the composition of the whole set by which components
    of which subsets were used. I want this class to refer to one group's make
    up. The chunk in reference to subsets that make up one group's part
    of the partition. So I think subpartition might be a better name. """
    pass

def get_subpartitions(group_name: VennSetName, state: VennGraph, handsize: int) -> [SubPartition]:
    """ Gets all valid subpartitions for a group given a graph and size.
    Will prioritize picking from the subset only it can take from first and
    build the rest of the combinations off of that. If it can't include
    all of the elements in the group only it can take from, or
    if there aren't enough elements outside of that group to fill
    its hand, then we return an empty list."""

    remainder = handsize - state.size(True, group_name)
    subset_sizes = sorted(list(state.get_subset_sizes(group_name).items()))
    if  remainder < 0: return []
    if remainder == 0: return [(group_name, handsize)]
    all_subpartitions = []
    for change in generate_changes(subset_sizes, remainder, 0, {ss[0]:0 for ss in subset_sizes}):
        change[group_name] = handsize-remainder
        all_subpartitions.append(change)

    return all_subpartitions


def get_partitions(state: VennGraph, handsizes: deque):
    size_state = {s:state._get_set_from_names(s).size() for s in state.get_all_set_names()}
    states = deque([size_state])
    while states:
        print(states)
        if not handsizes:
            return
        player, hand_size = handsizes.popleft()
        player_states_size = len(states)
        for _ in range(player_states_size):
            curr_state = states.popleft()
            for player_partition in get_subpartitions(player, curr_state, hand_size):
                states.append(apply_state_changes(player_partition, curr_state))



def apply_state_changes(option, state: VennGraph):
    """ Return a new VennGraph with the changes, or just modify
    the current graph. Let's try that. I just wouldn't want to edit it
    and have a bug that makes it so that we can't get it back to
    the original state."""
    pass

def generate_changes(sizes, hand_size, idx, res):
    if idx >= len(sizes) and hand_size != 0:
        return []
    if idx >= len(sizes) or hand_size == 0:
        yield res
        return res
    for i in range(sizes[idx][1] + 1):
        old_val = res[sizes[idx][0]]
        res[sizes[idx][0]] = i
        changes = generate_changes(sizes, hand_size - i, idx+1, res.copy())
        res[sizes[idx][0]] = old_val
        if changes:
            yield from changes


print("------------")

# for subpartition in get_subpartitions(p1, three_set_venn_diagram, 4):
#     print(subpartition)

get_partitions(three_set_venn_diagram, deque([[p1, 6]]))
