from bplustree import BPlusTree


def test_search_existing():
    tree = BPlusTree(order=4)
    tree.insert(42, "answer")
    assert tree.get(42) == "answer"


def test_search_nonexistent():
    tree = BPlusTree(order=4)
    tree.insert(1, "one")
    assert tree.get(2) is None


def test_search_large_tree():
    tree = BPlusTree(order=4)
    for i in range(100):
        tree.insert(i, f"val_{i}")
    for i in range(100):
        assert tree.get(i) == f"val_{i}"