
from VennElem import VennElem # type: ignore
type VennSetName = str | tuple[str, ...]
from typing import Any


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