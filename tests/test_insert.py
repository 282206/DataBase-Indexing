from bplustree import BPlusTree


def test_single_insert():
    tree = BPlusTree(order=4)
    tree.insert(10, "ten")
    assert tree.get(10) == "ten"


def test_multiple_inserts_sorted():
    tree = BPlusTree(order=4)
    for k in [30, 10, 20]:
        tree.insert(k, str(k))
    assert tree.root.keys == [10, 20, 30]


def test_insert_triggers_split():
    tree = BPlusTree(order=4)
    for k in [10, 20, 30, 40]:  # 4 keys → split happens
        tree.insert(k, str(k))
    assert not tree.root.is_leaf   # root should now be internal
    assert tree.root.keys == [30]


def test_get_after_split():
    tree = BPlusTree(order=4)
    for k in [10, 20, 30, 40, 50, 60]:
        tree.insert(k, str(k))
    for k in [10, 20, 30, 40, 50, 60]:
        assert tree.get(k) == str(k)


def test_get_missing_key():
    tree = BPlusTree(order=4)
    tree.insert(10, "ten")
    assert tree.get(99) is None