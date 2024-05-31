"""

        Set A        Set B        Set C
        /    \      /     \      /     \ 
  Set AC      Set AB       Set BC       Set AC
      |-----------\         /-------------|
                    Set ABC
"""


from collections import defaultdict
from typing import Any, Iterator
from itertools import combinations

type VennSetName = str | tuple[str, ...]
type GraphSet = dict[str, 'VennSet']


ALLOWED_VENN_GRAPH_SIZES = [2, 3]

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
            
            Given Sets A, B, C and an element x in set (A,B,C):
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
            ex: sets("A") -> ("A", "AB", "ABC")
        """
        return self._get_set_from_names(names).get_child_sets()



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


domino_map, all_dominoes = start_board()

print(all_dominoes)









p1 = "A"
p2 = "B"
p3 = "C"
three_set_venn_diagram = VennGraph(p1, p2, p3)
three_set_venn_diagram.add_to_set(all_dominoes, p1, p2, p3)



sets_related_to_a = three_set_venn_diagram.get_sets(p1)
sets_related_to_b = three_set_venn_diagram.get_sets(p2)
sets_related_to_c = three_set_venn_diagram.get_sets(p3)



three_set_venn_diagram.remove_from_graph([all_dominoes[0]])


for set_name, set_object in three_set_venn_diagram.sets.items():
    print(f'{set_object.name}: parents: {
          len(set_object.parents)} subsets: {len(set_object.subsets)} ' +
          f'value: {set_object.values}')



# start to think about the algorithm to use to determine what
# the outcomes might be

# play a domino... get the state...
# see which dominoes might possible with the current end points
# see what values would be available with each of those combinations
# find all possible applicable dominoes
# some dominoes might lead to similar states so merge those?
# figure out the math for how
# find what the probability would be for the ends to be certain digits.




# I just reduced all of the math I needed to do by looking at this
# as a partition problem.........


# the formula is number of partitions = Total Number of items in set! / (partition_1_size!, ..., partition_n_size!)