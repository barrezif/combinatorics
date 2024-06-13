from typing import Any

class VennElem:
    def __init__(self, wrapping):
        self.val: Any = wrapping
        self._curr_set = None

    def get_current_set(self):
        return self._curr_set

    def set_current_set(self, venn_set):
        self._curr_set = venn_set

    def clear_set(self):
        self._curr_set = None

    def __repr__(self):
        return f"VennElem({self.val})"