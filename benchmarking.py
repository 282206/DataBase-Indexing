import random
import sqlite3
import time
import bisect
import os
import matplotlib.pyplot as plt
from bplustree import BPlusTree


# ── config ──────────────────────────────────
N = 10_000        # number of keys to insert
ORDER = 50        # B+ tree order for benchmarking (bigger = faster)
SEED = 42
random.seed(SEED)

keys = random.sample(range(1, 1_000_000), N)
search_keys = random.sample(keys, min(1000, N))
range_pairs = [(random.randint(1, 900_000), random.randint(100_000, 1_000_000))
               for _ in range(50)]
range_pairs = [(min(a, b), max(a, b)) for a, b in range_pairs]


def time_it(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


# ── MiniDB ──────────────────────────────────
print("Running MiniDB benchmark...")
tree = BPlusTree(order=ORDER)

t_insert_mini = time_it(lambda: [tree.insert(k, str(k)) for k in keys])
t_search_mini = time_it(lambda: [tree.get(k) for k in search_keys])
t_range_mini  = time_it(lambda: [tree.range_query(s, e) for s, e in range_pairs])


# ── Python dict ─────────────────────────────
print("Running dict benchmark...")
d = {}

t_insert_dict = time_it(lambda: d.update({k: str(k) for k in keys}))
t_search_dict = time_it(lambda: [d.get(k) for k in search_keys])
t_range_dict  = time_it(lambda: [
    [(k, d[k]) for k in d if s <= k <= e]
    for s, e in range_pairs
])


# ── Sorted list (bisect) ─────────────────────
print("Running sorted list benchmark...")
sorted_keys = []
sorted_vals = []

def bisect_insert(k):
    i = bisect.bisect_left(sorted_keys, k)
    sorted_keys.insert(i, k)
    sorted_vals.insert(i, str(k))

def bisect_search(k):
    i = bisect.bisect_left(sorted_keys, k)
    if i < len(sorted_keys) and sorted_keys[i] == k:
        return sorted_vals[i]
    return None

def bisect_range(s, e):
    lo = bisect.bisect_left(sorted_keys, s)
    hi = bisect.bisect_right(sorted_keys, e)
    return list(zip(sorted_keys[lo:hi], sorted_vals[lo:hi]))

t_insert_bisect = time_it(lambda: [bisect_insert(k) for k in keys])
t_search_bisect = time_it(lambda: [bisect_search(k) for k in search_keys])
t_range_bisect  = time_it(lambda: [bisect_range(s, e) for s, e in range_pairs])


# ── SQLite ──────────────────────────────────
print("Running SQLite benchmark...")
if os.path.exists("sqlite_bench.db"):
    os.remove("sqlite_bench.db")

conn = sqlite3.connect("sqlite_bench.db")
cur = conn.cursor()
cur.execute("CREATE TABLE store (key INTEGER PRIMARY KEY, value TEXT)")
conn.commit()

def sqlite_insert():
    cur.executemany("INSERT INTO store VALUES (?, ?)",
                    [(k, str(k)) for k in keys])
    conn.commit()

def sqlite_search():
    for k in search_keys:
        cur.execute("SELECT value FROM store WHERE key=?", (k,))
        cur.fetchone()

def sqlite_range():
    for s, e in range_pairs:
        cur.execute("SELECT key, value FROM store WHERE key BETWEEN ? AND ?", (s, e))
        cur.fetchall()

t_insert_sql = time_it(sqlite_insert)
t_search_sql = time_it(sqlite_search)
t_range_sql  = time_it(sqlite_range)
conn.close()


# ── File sizes ──────────────────────────────
sqlite_size = os.path.getsize("sqlite_bench.db")
print(f"\nSQLite file size: {sqlite_size / 1024:.1f} KB")
print("(MiniDB disk size will be measured in Version 2)\n")


# ── Print results table ──────────────────────
print(f"{'Operation':<25} {'MiniDB':>10} {'Dict':>10} {'Bisect':>10} {'SQLite':>10}")
print("-" * 65)
print(f"{'Insert '+str(N)+' keys':<25} {t_insert_mini:>9.3f}s {t_insert_dict:>9.3f}s {t_insert_bisect:>9.3f}s {t_insert_sql:>9.3f}s")
print(f"{'Search 1k keys':<25} {t_search_mini:>9.3f}s {t_search_dict:>9.3f}s {t_search_bisect:>9.3f}s {t_search_sql:>9.3f}s")
print(f"{'Range queries x50':<25} {t_range_mini:>9.3f}s {t_range_dict:>9.3f}s {t_range_bisect:>9.3f}s {t_range_sql:>9.3f}s")


# ── Bar chart ────────────────────────────────
labels = ['Insert', 'Search', 'Range']
mini   = [t_insert_mini,   t_search_mini,   t_range_mini]
dct    = [t_insert_dict,   t_search_dict,   t_range_dict]
bis    = [t_insert_bisect, t_search_bisect, t_range_bisect]
sql    = [t_insert_sql,    t_search_sql,    t_range_sql]

x = range(len(labels))
width = 0.2

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar([i - 1.5*width for i in x], mini, width, label='MiniDB')
ax.bar([i - 0.5*width for i in x], dct,  width, label='Dict')
ax.bar([i + 0.5*width for i in x], bis,  width, label='Bisect')
ax.bar([i + 1.5*width for i in x], sql,  width, label='SQLite')

ax.set_ylabel('Time (seconds)')
ax.set_title(f'MiniDB Benchmark — {N} keys')
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.legend()
plt.tight_layout()
plt.savefig("benchmark_chart.png")
print("\nChart saved as benchmark_chart.png")


# ── Tree height vs N chart ───────────────────
sizes = [100, 500, 1000, 5000, 10000]
heights = []

for n in sizes:
    t = BPlusTree(order=ORDER)
    sample = random.sample(range(1, 1_000_000), n)
    for k in sample:
        t.insert(k, str(k))
    heights.append(t.get_height())

plt.figure(figsize=(8, 5))
plt.plot(sizes, heights, marker='o', color='steelblue')
plt.xlabel("Number of keys")
plt.ylabel("Tree height")
plt.title("B+ Tree Height vs N (should look logarithmic)")
plt.tight_layout()
plt.savefig("height_chart.png")
print("Height chart saved as height_chart.png")