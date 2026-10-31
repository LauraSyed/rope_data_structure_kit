"""A rope data structure for efficient storage and editing of long strings.

This package provides a single class, Rope, which stores a string as a balanced
binary tree of substrings.  The tree is kept balanced by a simple weight-based
concatenation that rebalances on demand.  The trade-off is that reads are
O(log n) instead of O(1) for a flat string, but insertions and deletions in the
middle of a very long string become O(log n) instead of O(n).
"""

from .core import Rope

__all__ = ["Rope"]
