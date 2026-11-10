from bplustree import BPlusTree


def test_basic_range():
    tree = BPlusTree(order=4)
    for k in [10, 20, 30, 40, 50]:
        tree.insert(k, str(k))
    result_keys = [k for k, v in tree.range_query(20, 40)]
    assert result_keys == [20, 30, 40]


def test_range_no_results():
    tree = BPlusTree(order=4)
    for k in [10, 20, 30]:
        tree.insert(k, str(k))
    assert tree.range_query(50, 100) == []


def test_range_all_keys():
    tree = BPlusTree(order=4)
    for k in [10, 20, 30]:
        tree.insert(k, str(k))
    result_keys = [k for k, v in tree.range_query(10, 30)]
    assert result_keys == [10, 20, 30]