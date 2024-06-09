"""

        Set A        Set B        Set C
        /    \      /     \      /     \ 
  Set AC      Set AB       Set BC       Set AC
      |-----------\         /-------------|
                    Set ABC
"""


from collections import defaultdict, deque
from typing import Any, Iterator
from itertools import combinations

type VennSetName = str | tuple[str, ...]
type GraphSet = dict[str, 'VennSet']


ALLOWED_VENN_GRAPH_SIZES = [2, 3, 8]

class VennSet:
    def __init__(self, name: VennSetName):
        self.values: list[VennElem] = []
        self.subsets: list['VennSet'] = []
        self.parents: list['VennSet'] = []
        self.name: VennSetName = name

    def add_value(self, values: 'VennElem'):
        values.set_current_set(self)
        self.values.append(values)

    def add_subsets(self, *subsets: VennSetName):
        self.subsets.extend(subsets)

    def add_parents(self, *parents: VennSetName):
        self.parents.extend(parents)

    def get_owners(self) -> set[VennSetName]:
        return set(self.name)

    def is_super_set_of(self, other) -> bool:
        return all(name in other.get_owners()
                   for name in self.get_owners())

    def contains_element(self, elem: [Any]) -> bool:
        return elem in self.values

    def __repr__(self): 
        return f'VennSet("{self.name} values=[{self.values}]")'

    def get_elements(self, strict=True):
        if strict:
            return self.values
        child_elements = set(val for child in self.subsets for val in child.get_elements(strict))
        return child_elements | set(self.values)

    def size(self, strict=True):
        if strict:
            return len(self.values)
        return len(self.get_elements(strict)) + len(self.values)

    def get_child_sets(self):
        return list(set(s for child in self.subsets for s in child.get_child_sets())) + [self.name]

class VennElem:
    def __init__(self, wrapping):
        self.val: Any = wrapping
        self._curr_set: VennSet = None

    def get_current_set(self) -> VennSet:
        return self._curr_set

    def set_current_set(self, venn_set: VennSet):
        self._curr_set = venn_set

    def clear_set(self):
        self._curr_set = None

    def __repr__(self):
        return f"VennElem({self.val})"


class VennGraph:
    """ Class that represents a Venn Diagram
    
    Provides methods to add/remove elements to/from different
    sets within the Venn Diagram and methods to get the elements
    in the given sets.
    """

    def __init__(self, *names: str):
        self.sets: GraphSet = self._create_sets_from_names(list(sorted(names)))
        self.parent_sets: list[VennSetName] = list(sorted(names))
        self._element_registry = {}

    def _create_sets_from_names(self,
                                names: list[VennSetName]) -> GraphSet:
        """ Creates VennSet objects from list of names """
        if len(names) not in ALLOWED_VENN_GRAPH_SIZES:
            raise ValueError("Can only create VennGraph for 2 or 3 sets")

        set_names_by_level = self._generate_intersection_names(names)

        venn_sets: GraphSet = {}

        parent_level: list[VennSet] = []

        for level in set_names_by_level:
            curr_names: list[VennSet] = []
            for set_name in level:
                venn_sets[set_name] = VennSet(set_name)
                for parent in parent_level:
                    if parent.is_super_set_of(venn_sets[set_name]):
                        venn_sets[set_name].add_parents(parent)
                        parent.add_subsets(venn_sets[set_name])
                curr_names.append(venn_sets[set_name])
            parent_level = curr_names

        return venn_sets

    def _register_and_get(self, elem: Any) -> VennElem:
        """ Wraps element in VennElem """
        if elem not in self._element_registry:
            self._element_registry[elem] = VennElem(elem)
        return self._element_registry[elem]

    def _generate_intersection_names(
            self, names: list[VennSetName]) -> list[list[VennSetName]]:
        """ Creates all intersection subset names for the graph. """

        return [res for i in range(1, len(names)+1)
                if (res := combinations(names, i))]

    def _get_set_from_names(
            self, names: list[VennSetName]) -> VennSet:
        """ Returns VennSetName associated with given sets or throws """

        hashed_name = tuple(sorted(names))
        if hashed_name not in self.sets:
            raise ValueError(
                f"Given set {hashed_name} does not exist in graph\n" +
                f"Set names are {'-'.join(str(name) for name in self.sets)}")

        return self.sets[hashed_name]

    def add_to_set(self, elems: [Any], *names: VennSetName):
        """ Adds elements to the set matching the union of the given sets
            
            Given Sets A, B, C and an element x in set (A,):
            * adding to set (B,) results in the element being
            moves to set (A,B)
            * adding to set (B,C) results in the element being
            moved to set (A,B,C)
        """
        for elem in elems:
            registered = self._register_and_get(elem)
            if registered.get_current_set():
                names = list(set(names)
                             | registered.get_current_set().get_owners())
                self._remove_from_set(registered)
            venn_set = self._get_set_from_names(names)
            venn_set.add_value(registered)

    def put_in_set(self, elems: [Any], *names: VennSetName):
        """ Moves elements to set matching the intersection of the names """
        venn_set = self._get_set_from_names(list(names))
        for elem in elems:
            registered = self._register_and_get(elem)
            if registered.get_current_set():
                self._remove_from_set(registered)
            venn_set.add_value(registered)

    def _remove_from_set(self, registered_elem: VennElem):
        """ Removes connection between VennElem <-> VennSet """
        curr_set = registered_elem.get_current_set()
        curr_set.values.remove(registered_elem)
        registered_elem.clear_set()

    def remove_from_set(self, elems: [Any],
                        names: [VennSetName]):
        """ Removes an element from the sets provided

            Given Sets A, B, C and an element x in set (A,B,C):
            * removing from set (A,) would result in the element
            being moved to set (B,C).
            * removing from set (A,B) would result in the element
            being moved to set (C,)
            * removing from set (A,B,C) would result in the element
            being removed from the graph altogether.
        """

        for elem in elems:
            registered_elem = self._get_from_registry(elem)
            if not registered_elem:
                continue
            venn_set = self._get_set_from_names(list(names)) if names else \
                registered_elem.get_current_set()

            new_name = registered_elem.get_current_set().get_owners() - \
                venn_set.get_owners()
            self._remove_from_set(registered_elem)
            if not tuple(list(new_name)):
                self._remove_from_graph(registered_elem)
            else:
                new_venn = self._get_set_from_names(new_name)
                new_venn.add_value(registered_elem)

    def get_parent_sets(self):
        return self.parent_sets

    def _get_from_registry(self, elem: Any)->VennElem:
        if elem in self._element_registry:
            return self._element_registry[elem]
        return None

    def _remove_from_graph(self, registered_elem: Any):
        del self._element_registry[registered_elem]

    def remove_from_graph(self, elems: [Any]):
        """ Removes an element from the venn diagram """
        for elem in elems:
            registered = self._register_and_get(elem)
            self._remove_from_set(registered)
            self._remove_from_graph(elem)

    def get_elements_in_set(self, *names: VennSetName):
        """ Returns all elements in given set """
        venn_set = self._get_set_from_names(list(names))
        for val in venn_set.values:
            yield val.val

    def size(self, inclusive:bool, *names: VennSetName) -> int:
        """ Returns the size of the current"""
        return self._get_set_from_names(names).size(inclusive)

    def get_sets(self, *names: VennSetName)->Iterator[VennSet]:
        """ A generator for sets that include the given set
            ex: sets("A") -> ("A", "AB", "AC", "ABC")
        """
        return self._get_set_from_names(names).get_child_sets()

    def get_subset_sizes(self, *names:VennSetName): # Map of name:size
        """ Returns a dict of the subset name to size of the subset"""
        child_sets = self._get_set_from_names(names).get_child_sets()
        for child in child_sets:
            print(child)
        return {child: self._get_set_from_names(child).size() for child in child_sets if child != names}




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


# for set_name, set_object in three_set_venn_diagram.sets.items():
#     print(f'{set_object.name}: parents: {
#           len(set_object.parents)} subsets: {len(set_object.subsets)} ' +
#           f'value: {set_object.values}')


class GraphAction:
    """IDK, a number and a zone in the graph, a group name, to modify the graph"""
    pass

# Subpartition?
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
    print("This is the subset sizes map", subset_sizes)
    if  remainder < 0: return []
    if remainder == 0: return [(group_name, handsize)]
    all_subpartitions = []
    for change in generate_changes(subset_sizes, remainder, 0, {ss[0]:0 for ss in subset_sizes}):
        change[group_name] = handsize-remainder
        all_subpartitions.append(change)
    # It would be easy if I could just hash the names of these sets. I need
    # a good and consistent way to do that. I've been sorting things lexigraphically
    # and using the string of the concatted group names as the name, but I'm
    # not sure if that's prone to causing some bugs in the future.
    # anyways, I want to dynamically get the remaining group names
    # with the number of items in those groups, and find all possible ways
    # this group can pick elements from those subgroups without the
    # remainder going below 0. I think doing this recursively is the best
    # option.

    return all_subpartitions


def get_partitions(state: VennGraph, handsizes: deque):
    size_state = SizeVennGraph(state) # represent the graph with just the number
                                      # of elems in each set instead of the objects
    states = deque([size_state])
    while states:
        player, hand_size = handsizes.popleft()
        player_states_size = len(states)
        for _ in range(player_states_size):
            curr_state = states.popleft()
            for player_partition in get_subpartitions(player, curr_state, hand_size):
                states.append(apply_state_changes(player_partition, curr_state))



def apply_state_changes(option: GraphAction, state: VennGraph):
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

for subpartition in get_subpartitions(p1, three_set_venn_diagram, 4):
    print(subpartition)

# Since (A, B, C) comes before (A,C), we don't see the full SubPartition,
# Need to fix that logic so that we see all of the subsets in the result.


# p4 = "D"
# p5 = "E"
# p6 = "F"
# p7 = "G"
# p8 = "H"
# eight_set_venn_graph = VennGraph(p1, p2, p3, p4, p5, p6, p7 ,p8)
# eight_set_venn_graph.add_to_set(all_dominoes, p1, p2, p3, p4, p5, p6, p7 ,p8)

# for set_name, set_object in eight_set_venn_graph.sets.items():
#     print(f'{set_object.name}: parents: {
#           len(set_object.parents)} subsets: {len(set_object.subsets)} ' +
#           f'value: {set_object.values}')