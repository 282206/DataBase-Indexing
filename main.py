import json
import os

from bplustree import BPlusTree


def print_tree(tree):
    print("\n===== B+ Tree Structure =====")
    current_level = [tree.root]
    level_num = 0

    while current_level:
        next_level = []
        level_str = f"Level {level_num}: "
        for node in current_level:
            label = "LEAF" if node.is_leaf else "NODE"
            level_str += f"{label}{node.keys}  "
            if not node.is_leaf:
                next_level.extend(node.children)
        print(level_str)
        current_level = next_level
        level_num += 1

    print("\n--- Leaf chain ---")
    leaf = tree.root
    while not leaf.is_leaf:
        leaf = leaf.children[0]
    chain = []
    while leaf:
        chain.append(str(leaf.keys))
        leaf = leaf.next
    print(" → ".join(chain))
    print("=========================\n")


if __name__ == "__main__":
    print("=" * 40)
    print("  MiniDB — B+ Tree Demo")
    print("=" * 40)

    # ── Basic insert demo ────────────────────
    tree = BPlusTree(order=4)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
    print(f"\nInserting keys: {keys}")
    for k in keys:
        tree.insert(k, str(k))

    print_tree(tree)
    print(f"Height      : {tree.get_height()}")
    print(f"get(12)     : {tree.get(12)}")
    print(f"Range 6–17  : {tree.range_query(6, 17)}")

    # ── JSON loading demo ────────────────────
    sample_path = "sample_data.json"
    sample = [{"key": k, "value": f"item_{k}"} for k in [100, 200, 150, 50, 250, 175, 125]]
    with open(sample_path, "w") as f:
        json.dump(sample, f, indent=2)

    print(f"\n{'─'*40}")
    print(f"Loading from {sample_path} (list format) …")
    tree2 = BPlusTree(order=4)
    tree2.load_json(sample_path)
    print_tree(tree2)
    print(f"get(150)        : {tree2.get(150)}")
    print(f"Range 100–175   : {tree2.range_query(100, 175)}")

    os.remove(sample_path)

    # ── Dict-format JSON demo ────────────────
    dict_path = "dict_data.json"
    with open(dict_path, "w") as f:
        json.dump({"5": "five", "3": "three", "8": "eight", "1": "one", "7": "seven"}, f)

    print(f"\n{'─'*40}")
    print(f"Loading from {dict_path} (dict format) …")
    tree3 = BPlusTree(order=4)
    tree3.load_json(dict_path)
    print_tree(tree3)
    print(f"get(8)        : {tree3.get(8)}")

    os.remove(dict_path)
