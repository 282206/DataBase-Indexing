import os
import json
import tempfile

from bplustree import BPlusTree


def _write_temp_json(data):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(data, f)
    f.close()
    return f.name


def test_load_json_list_format():
    path = _write_temp_json([
        {"key": 10, "value": "ten"},
        {"key": 5,  "value": "five"},
        {"key": 20, "value": "twenty"},
    ])
    try:
        tree = BPlusTree(order=4)
        tree.load_json(path)
        assert tree.get(10) == "ten"
        assert tree.get(5)  == "five"
        assert tree.get(20) == "twenty"
        assert tree.get(99) is None
    finally:
        os.unlink(path)


def test_load_json_dict_format():
    path = _write_temp_json({"10": "ten", "20": "twenty", "30": "thirty"})
    try:
        tree = BPlusTree(order=4)
        tree.load_json(path)
        assert tree.get(10) == "ten"
        assert tree.get(20) == "twenty"
        assert tree.get(30) == "thirty"
    finally:
        os.unlink(path)


def test_load_json_range_query():
    data = [{"key": k, "value": str(k)} for k in range(1, 21)]
    path = _write_temp_json(data)
    try:
        tree = BPlusTree(order=4)
        tree.load_json(path)
        result_keys = [k for k, v in tree.range_query(5, 10)]
        assert result_keys == [5, 6, 7, 8, 9, 10]
    finally:
        os.unlink(path)


def test_load_json_triggers_splits():
    data = [{"key": k, "value": str(k)} for k in range(20)]
    path = _write_temp_json(data)
    try:
        tree = BPlusTree(order=4)
        tree.load_json(path)
        assert not tree.root.is_leaf
        for k in range(20):
            assert tree.get(k) == str(k)
    finally:
        os.unlink(path)
