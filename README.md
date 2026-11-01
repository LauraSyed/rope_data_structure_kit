# rope_data_structure_kit

A rope data structure that stores and edits long strings as a balanced tree of substrings.

```python
from rope_data_structure_kit import Rope

r = Rope("hello world")
r = r.insert(5, ",")
print(r.to_string())          # hello, world
print(r[0])                   # h
print(len(r))                 # 12

r = r.delete(5, 6)
print(r.to_string())          # hello world

r = r.replace(6, 11, "there")
print(r.to_string())          # hello there
print(r.substring(0, 5))      # hello
```

## Why this library exists

Editing a very long string with plain Python string operations is O(n) per edit
because the whole string is copied.  A rope stores the string as a balanced
binary tree of substrings, so indexing and splitting are O(log n).  The
trade-off is that reads are slower than a flat string and the tree must be
rebuilt after structural changes; we accept that cost because the library is
meant for workloads with many edits to large strings.

## The awkward edge

Negative indices are not supported.  In a rope, negative indexing would require
knowing the total length before descending, which defeats the purpose of the
tree.  We raise `IndexError` for negative indices so the behaviour is explicit
rather than silently wrong.

## API

- `Rope(initial: str = "")`
- `len(rope)`
- `rope[index]`
- `rope.to_string() -> str`
- `rope.insert(index: int, text: str) -> Rope`
- `rope.delete(start: int, end: int) -> Rope`
- `rope.replace(start: int, end: int, text: str) -> Rope`
- `rope.substring(start: int, end: int) -> str`

All mutation methods return a new `Rope`; the original is unchanged.
