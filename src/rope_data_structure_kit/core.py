"""Core implementation of the rope data structure.

The rope is a binary tree where each leaf holds a string.  Internal nodes hold
the total length of their left subtree so that indexing and splitting can be
done in O(log n).  We deliberately keep the tree balanced by rebuilding the
whole tree after every mutation that changes the structure.  This is simple and
predictable; the alternative (incremental rebalancing) is more complex and
harder to test.  Rebuilding is O(n) but only happens on writes, while reads
remain O(log n).
"""

from __future__ import annotations

from typing import List, Optional


class _Node:
    """A node in the rope tree.

    Leaves have ``left is None`` and ``right is None`` and store a string in
    ``data``.  Internal nodes have two children and store the length of the
    left subtree in ``weight``.  ``data`` is unused for internal nodes.
    """

    __slots__ = ("weight", "data", "left", "right")

    def __init__(
        self,
        weight: int,
        data: Optional[str] = None,
        left: Optional[_Node] = None,
        right: Optional[_Node] = None,
    ) -> None:
        self.weight = weight
        self.data = data
        self.left = left
        self.right = right


def _leaf(s: str) -> _Node:
    return _Node(len(s), data=s)


def _concat(left: _Node, right: _Node) -> _Node:
    """Join two trees, preserving the invariant that weight is the length of
    the left subtree."""
    return _Node(_length(left), left=left, right=right)


def _build_balanced(parts: List[str]) -> _Node:
    """Build a balanced rope from a list of strings.

    We split the list in half recursively so the tree height is O(log n).
    Empty strings are skipped to avoid useless leaves.
    """
    if not parts:
        return _leaf("")
    if len(parts) == 1:
        return _leaf(parts[0])
    mid = len(parts) // 2
    left = _build_balanced(parts[:mid])
    right = _build_balanced(parts[mid:])
    return _concat(left, right)


def _collect(node: _Node, out: List[str]) -> None:
    """Flatten the tree into a list of leaf strings in order."""
    if node.left is None and node.right is None:
        if node.data:
            out.append(node.data)
        return
    _collect(node.left, out)
    _collect(node.right, out)


def _index(node: _Node, i: int) -> str:
    """Return the character at index i (0-based)."""
    if node.left is None and node.right is None:
        return node.data[i]
    if i < node.weight:
        return _index(node.left, i)
    return _index(node.right, i - node.weight)


def _split(node: _Node, i: int) -> tuple[_Node, _Node]:
    """Split the tree at index i, returning (left, right).

    The split is done by flattening to a list of leaf strings and then
    rebuilding two balanced trees.  This is O(n) but keeps the code simple and
    correct; a production rope would split the tree directly.
    """
    if i <= 0:
        return _leaf(""), node
    total = _length(node)
    if i >= total:
        return node, _leaf("")
    parts: List[str] = []
    _collect(node, parts)
    # Find the leaf containing the split point.
    left_parts: List[str] = []
    right_parts: List[str] = []
    remaining = i
    for part in parts:
        if remaining <= 0:
            right_parts.append(part)
        elif remaining >= len(part):
            left_parts.append(part)
            remaining -= len(part)
        else:
            left_parts.append(part[:remaining])
            right_parts.append(part[remaining:])
            remaining = 0
    return _build_balanced(left_parts), _build_balanced(right_parts)


def _length(node: _Node) -> int:
    """Total number of characters in the subtree."""
    if node.left is None and node.right is None:
        return len(node.data) if node.data else 0
    return _length(node.left) + _length(node.right)


class Rope:
    """A rope data structure for efficient storage and editing of long strings.

    The rope is immutable from the caller's perspective: every mutation returns
    a new Rope.  This makes it safe to share subtrees and simplifies reasoning
    about the structure.  The trade-off is that every write allocates a new
    tree, but the tree is balanced so the allocation is proportional to the
    string length, not the edit distance.

    Example::

        from rope_data_structure_kit import Rope
        r = Rope("hello world")
        r = r.insert(5, ",")
        assert r.to_string() == "hello, world"
    """

    __slots__ = ("_root",)

    def __init__(self, initial: str = "") -> None:
        """Create a rope from an initial string.

        The string is split into fixed-size chunks to keep leaves small and
        the tree balanced.  A chunk size of 16 is a compromise: small enough
        that splits and joins are cheap, large enough that the tree does not
        become too deep.
        """
        if not isinstance(initial, str):
            raise TypeError("initial must be a string")
        chunk = 16
        parts = [initial[i : i + chunk] for i in range(0, len(initial), chunk)]
        if not parts:
            parts = [""]
        self._root = _build_balanced(parts)

    def __len__(self) -> int:
        """Return the number of characters in the rope."""
        return _length(self._root)

    def __getitem__(self, index: int) -> str:
        """Return the character at the given index.

        Negative indices are not supported; they raise IndexError to avoid
        surprising behaviour in a data structure that is meant for large
        strings where negative indexing is rarely useful.
        """
        if not isinstance(index, int):
            raise TypeError("index must be an integer")
        n = len(self)
        if index < 0 or index >= n:
            raise IndexError("rope index out of range")
        return _index(self._root, index)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rope):
            return NotImplemented
        return self.to_string() == other.to_string()

    def __repr__(self) -> str:
        return f"Rope({self.to_string()!r})"

    def to_string(self) -> str:
        """Return the full string represented by the rope."""
        parts: List[str] = []
        _collect(self._root, parts)
        return "".join(parts)

    def insert(self, index: int, text: str) -> "Rope":
        """Return a new rope with ``text`` inserted at ``index``.

        ``index`` may be equal to the length, in which case the text is
        appended.  Negative indices are not supported.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        n = len(self)
        if index < 0 or index > n:
            raise IndexError("insert index out of range")
        left, right = _split(self._root, index)
        new_root = _concat(_concat(left, _leaf(text)), right)
        result = Rope.__new__(Rope)
        result._root = new_root
        return result

    def delete(self, start: int, end: int) -> "Rope":
        """Return a new rope with the characters in ``[start, end)`` removed.

        ``start`` and ``end`` must satisfy ``0 <= start <= end <= len(self)``.
        """
        n = len(self)
        if start < 0 or end < start or end > n:
            raise IndexError("delete range out of bounds")
        left, rest = _split(self._root, start)
        _, right = _split(rest, end - start)
        new_root = _concat(left, right)
        result = Rope.__new__(Rope)
        result._root = new_root
        return result

    def replace(self, start: int, end: int, text: str) -> "Rope":
        """Return a new rope with ``[start, end)`` replaced by ``text``."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        n = len(self)
        if start < 0 or end < start or end > n:
            raise IndexError("replace range out of bounds")
        left, rest = _split(self._root, start)
        _, right = _split(rest, end - start)
        new_root = _concat(_concat(left, _leaf(text)), right)
        result = Rope.__new__(Rope)
        result._root = new_root
        return result

    def substring(self, start: int, end: int) -> str:
        """Return the substring ``[start, end)`` as a plain string."""
        n = len(self)
        if start < 0 or end < start or end > n:
            raise IndexError("substring range out of bounds")
        if start == end:
            return ""
        # For simplicity and correctness we flatten and slice.  A production
        # rope would descend the tree and collect only the needed leaves.
        return self.to_string()[start:end]
