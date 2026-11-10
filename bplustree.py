import json


# ─────────────────────────────────────────
# NODES
# ─────────────────────────────────────────

class Node:
    is_leaf = False

    def __init__(self):
        self.keys = []
        self.parent = None


class LeafNode(Node):
    is_leaf = True

    def __init__(self):
        super().__init__()
        self.values = []
        self.next = None


class InternalNode(Node):
    def __init__(self):
        super().__init__()
        self.children = []


class BPlusTree:
    def __init__(self, order=4):
        self.root = LeafNode()
        self.order = order

    # ─────────────────────────────────────────
    # SEARCH
    # ─────────────────────────────────────────

    def _find_leaf(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        return node

    def get(self, key):
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None

    # ─────────────────────────────────────────
    # INSERT
    # ─────────────────────────────────────────

    def insert(self, key, value):
        leaf = self._find_leaf(key)
        self._insert_into_leaf(leaf, key, value)
        if len(leaf.keys) >= self.order:
            self._split_leaf(leaf)

    def _insert_into_leaf(self, leaf, key, value):
        i = 0
        while i < len(leaf.keys) and leaf.keys[i] < key:
            i += 1
        leaf.keys.insert(i, key)
        leaf.values.insert(i, value)

    # ─────────────────────────────────────────
    # SPLITTING
    # ─────────────────────────────────────────

    def _split_leaf(self, leaf):
        mid = len(leaf.keys) // 2

        new_leaf = LeafNode()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]

        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        new_leaf.next = leaf.next
        leaf.next = new_leaf

        push_up_key = new_leaf.keys[0]

        if leaf is self.root:
            new_root = InternalNode()
            new_root.keys = [push_up_key]
            new_root.children = [leaf, new_leaf]
            self.root = new_root
        else:
            parent = self._find_parent(self.root, leaf)
            self._insert_into_internal(parent, push_up_key, new_leaf)
            if len(parent.keys) >= self.order:
                self._split_internal(parent)

    def _split_internal(self, node):
        mid = len(node.keys) // 2
        push_up_key = node.keys[mid]

        new_node = InternalNode()
        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]

        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        if node is self.root:
            new_root = InternalNode()
            new_root.keys = [push_up_key]
            new_root.children = [node, new_node]
            self.root = new_root
        else:
            parent = self._find_parent(self.root, node)
            self._insert_into_internal(parent, push_up_key, new_node)
            if len(parent.keys) >= self.order:
                self._split_internal(parent)

    def _insert_into_internal(self, node, key, right_child):
        i = 0
        while i < len(node.keys) and node.keys[i] < key:
            i += 1
        node.keys.insert(i, key)
        node.children.insert(i + 1, right_child)

    def _find_parent(self, current, target_child):
        if current.is_leaf:
            return None
        for child in current.children:
            if child is target_child:
                return current
        for child in current.children:
            result = self._find_parent(child, target_child)
            if result:
                return result
        return None

    # ─────────────────────────────────────────
    # RANGE QUERY
    # ─────────────────────────────────────────

    def range_query(self, start_key, end_key):
        results = []
        leaf = self._find_leaf(start_key)
        while leaf is not None:
            for i, key in enumerate(leaf.keys):
                if key > end_key:
                    return results
                if key >= start_key:
                    results.append((key, leaf.values[i]))
            leaf = leaf.next
        return results

    # ─────────────────────────────────────────
    # JSON LOADING
    # ─────────────────────────────────────────

    def load_json(self, filepath):
        """
        Load key-value pairs from a JSON file.

        Supports two formats:
          - List:  [{"key": 1, "value": "one"}, ...]
          - Dict:  {"1": "one", "2": "two", ...}
        """
        with open(filepath) as f:
            data = json.load(f)

        if isinstance(data, list):
            for item in data:
                self.insert(item["key"], item["value"])
        elif isinstance(data, dict):
            for k, v in data.items():
                try:
                    k = int(k)
                except (ValueError, TypeError):
                    pass
                self.insert(k, v)
        return self

    # ─────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────

    def get_height(self):
        height = 0
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
            height += 1
        return height
