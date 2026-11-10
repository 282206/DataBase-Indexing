# MiniDB

A B+ tree based key-value storage engine written from scratch in Python.

## Project Structure

```
minidb/
├── bplustree.py      # Node / LeafNode / InternalNode + BPlusTree (search, insert, split, range, JSON)
├── main.py           # Demo runner and tree printer
├── benchmarking.py   # Performance comparison vs dict, bisect, SQLite
└── tests/
    ├── conftest.py   # Shared pytest path setup
    ├── test_insert.py
    ├── test_search.py
    ├── test_range.py
    └── test_json.py
```

## Quick Start

```python
from bplustree import BPlusTree

tree = BPlusTree(order=4)
tree.insert(10, "ten")
tree.insert(20, "twenty")
tree.insert(5, "five")

print(tree.get(10))                  # "ten"
print(tree.range_query(5, 15))       # [(5, 'five'), (10, 'ten')]
print(tree.get_height())             # 1
```

## JSON Loading

`load_json` supports two formats:

**List format** (recommended)
```json
[
  {"key": 1, "value": "one"},
  {"key": 2, "value": "two"}
]
```

**Dict format**
```json
{"1": "one", "2": "two"}
```

```python
tree = BPlusTree(order=50)
tree.load_json("data.json")
```

String keys that are valid integers are automatically cast.

## Running

```bash
# Demo with tree printout and JSON loading
python3 main.py

# Full test suite (15 tests)
python3 -m pytest tests/ -v

# Benchmark vs dict, bisect, SQLite — saves benchmark_chart.png + height_chart.png
python3 benchmarking.py
```

## API Reference

| Method | Description |
|---|---|
| `insert(key, value)` | Insert a key-value pair; splits nodes when full |
| `get(key)` | Return value for key, or `None` if absent |
| `range_query(lo, hi)` | Return `[(key, value), …]` for all keys in `[lo, hi]` |
| `load_json(filepath)` | Bulk-load from a JSON file (list or dict format) |
| `get_height()` | Count levels from root to leaf |

## Benchmark Results (N = 10,000 keys, order = 50)

| Operation | MiniDB | Dict | Bisect | SQLite |
|---|---|---|---|---|
| Insert 10k keys | ~0.041s | ~0.001s | ~0.047s | ~0.014s |
| Search 1k keys | ~0.003s | ~0.000s | ~0.000s | ~0.008s |
| Range queries ×50 | ~0.027s | ~0.056s | ~0.011s | ~0.082s |

MiniDB's leaf chain makes range queries faster than both Python dict (full scan) and SQLite, at the cost of slower point lookups versus a hash map.

## How Splits Work

- **Leaf split**: when a leaf reaches `order` keys, split at midpoint, copy right half to new leaf, push the smallest right key up to the parent.
- **Internal split**: when an internal node reaches `order` keys, split at midpoint, push the middle key up, keep left/right children on each side.
- Both propagate upward recursively; a new root is created when the current root splits.
