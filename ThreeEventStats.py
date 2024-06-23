from VennGraph import VennGraph
from VennElem import VennElem
from VennSet import VennSet
from collections import defaultdict, deque

type VennSetName = str | tuple[str, ...]
type GraphSet = dict[str, 'VennSet']


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

def get_subpartitions(group_name, state: VennGraph, handsize: int):
    """ Gets all valid subpartitions for a group given a graph and size.
    Will prioritize picking from the subset only it can take from first and
    build the rest of the combinations off of that. If it can't include
    all of the elements in the group only it can take from, or
    if there aren't enough elements outside of that group to fill
    its hand, then we return an empty list."""

    this_set_size = 0
    this_subsets = []
    not_this_subsets = []

    for sub_graph in state.keys():
        if tuple(group_name) == sub_graph:
            this_set_size = state[sub_graph]
        elif group_name in sub_graph:
            this_subsets.append([sub_graph, state[sub_graph]])
        else:
            not_this_subsets.append([sub_graph, state[sub_graph]])

    remainder = handsize - this_set_size
    subset_sizes = sorted(this_subsets)
    if remainder < 0:
        return []
    if remainder == 0:
        return [(group_name, handsize)]
    all_subpartitions = []
    for change in generate_changes(subset_sizes, remainder, 0, {ss[0]: 0 for ss in subset_sizes}):
        change[(group_name,)] = handsize-remainder
        all_subpartitions.append(change)

    return all_subpartitions


def get_partitions(state: VennGraph, handsizes: deque):
    size_state = {s: state._get_set_from_names(
        s).size() for s in state.get_all_set_names()}
    states = deque([size_state])
    partitions = deque([[]])
    while states:
        if not handsizes:
            return partitions
        player, hand_size = handsizes.popleft()
        player_states_size = len(states)
        for _ in range(player_states_size):
            curr_state = states.popleft()
            curr_partition = partitions.popleft()
            for player_partition in get_subpartitions(player, curr_state, hand_size):
                partition_copy = curr_partition.copy()
                partition_copy.append(player_partition)
                partitions.append(partition_copy)
                states.append(apply_state_changes(
                    player_partition, curr_state.copy()))



def apply_state_changes(changes, state: VennGraph):
    """ Return a new VennGraph with the changes"""
    for k, v in changes.items():
        state[k] = state[k] - v
    return state


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

for partition in get_partitions(three_set_venn_diagram, deque([[p1, 6], [p2, 6], [p3,6]])):
    print("========================")
    print(partition)


















"""
The Data is the collection of subsets that make up the venn diagram, the mapping of
dominoes to venn diagram subset, and the number of elements each parent set must have
to make their hand.


Parent Sets -> Subsets
Subsets -> Dominos
A combination is 




"""