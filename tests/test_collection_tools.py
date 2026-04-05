"""Comprehensive tests for collection tools."""

import asyncio
import json

import pytest
from mcp.server.fastmcp import FastMCP


def _make_server():
    mcp = FastMCP(name="test")
    from tools.collection_tools import register

    register(mcp)
    return mcp


def _call(mcp, name, args):
    result = asyncio.run(mcp.call_tool(name, args))
    # call_tool returns (content_list, extra) tuple in this version
    content = result[0] if isinstance(result, tuple) else result
    return json.loads(content[0].text)


# ── collection_sort ──────────────────────────────────────────────────────────


class TestCollectionSort:
    def setup_method(self):
        self.mcp = _make_server()

    def test_sort_integers(self):
        res = _call(self.mcp, "collection_sort", {"items": [3, 1, 2]})
        assert res == {"result": [1, 2, 3]}

    def test_sort_strings(self):
        res = _call(self.mcp, "collection_sort", {"items": ["banana", "apple", "cherry"]})
        assert res == {"result": ["apple", "banana", "cherry"]}

    def test_sort_reverse(self):
        res = _call(self.mcp, "collection_sort", {"items": [1, 3, 2], "reverse": True})
        assert res == {"result": [3, 2, 1]}

    def test_sort_empty(self):
        res = _call(self.mcp, "collection_sort", {"items": []})
        assert res == {"result": []}

    def test_sort_single_element(self):
        res = _call(self.mcp, "collection_sort", {"items": [42]})
        assert res == {"result": [42]}

    def test_sort_already_sorted(self):
        res = _call(self.mcp, "collection_sort", {"items": [1, 2, 3]})
        assert res == {"result": [1, 2, 3]}

    def test_sort_floats(self):
        res = _call(self.mcp, "collection_sort", {"items": [3.14, 1.41, 2.72]})
        assert res == {"result": [1.41, 2.72, 3.14]}

    def test_sort_duplicates(self):
        res = _call(self.mcp, "collection_sort", {"items": [2, 1, 2, 3, 1]})
        assert res == {"result": [1, 1, 2, 2, 3]}


# ── collection_flatten ───────────────────────────────────────────────────────


class TestCollectionFlatten:
    def setup_method(self):
        self.mcp = _make_server()

    def test_flatten_nested(self):
        res = _call(self.mcp, "collection_flatten", {"items": [1, [2, 3], [4, [5, 6]]]})
        assert res == {"result": [1, 2, 3, 4, 5, 6]}

    def test_flatten_already_flat(self):
        res = _call(self.mcp, "collection_flatten", {"items": [1, 2, 3]})
        assert res == {"result": [1, 2, 3]}

    def test_flatten_empty(self):
        res = _call(self.mcp, "collection_flatten", {"items": []})
        assert res == {"result": []}

    def test_flatten_deeply_nested(self):
        res = _call(self.mcp, "collection_flatten", {"items": [[[[[1]]]]]})
        assert res == {"result": [1]}

    def test_flatten_mixed_types(self):
        res = _call(self.mcp, "collection_flatten", {"items": [1, "a", [2, "b", [3]]]})
        assert res == {"result": [1, "a", 2, "b", 3]}

    def test_flatten_empty_sublists(self):
        res = _call(self.mcp, "collection_flatten", {"items": [[], [1], [], [2, []], 3]})
        assert res == {"result": [1, 2, 3]}


# ── collection_merge ─────────────────────────────────────────────────────────


class TestCollectionMerge:
    def setup_method(self):
        self.mcp = _make_server()

    def test_merge_no_conflict(self):
        res = _call(
            self.mcp, "collection_merge", {"dict_a": {"a": 1}, "dict_b": {"b": 2}}
        )
        assert res == {"result": {"a": 1, "b": 2}}

    def test_merge_with_conflict(self):
        res = _call(
            self.mcp,
            "collection_merge",
            {"dict_a": {"a": 1, "b": 2}, "dict_b": {"b": 99, "c": 3}},
        )
        assert res == {"result": {"a": 1, "b": 99, "c": 3}}

    def test_merge_empty_a(self):
        res = _call(self.mcp, "collection_merge", {"dict_a": {}, "dict_b": {"x": 1}})
        assert res == {"result": {"x": 1}}

    def test_merge_empty_b(self):
        res = _call(self.mcp, "collection_merge", {"dict_a": {"x": 1}, "dict_b": {}})
        assert res == {"result": {"x": 1}}

    def test_merge_both_empty(self):
        res = _call(self.mcp, "collection_merge", {"dict_a": {}, "dict_b": {}})
        assert res == {"result": {}}

    def test_merge_b_wins_all_conflicts(self):
        res = _call(
            self.mcp,
            "collection_merge",
            {"dict_a": {"k": "old"}, "dict_b": {"k": "new"}},
        )
        assert res["result"]["k"] == "new"


# ── collection_filter_gt ─────────────────────────────────────────────────────


class TestCollectionFilterGt:
    def setup_method(self):
        self.mcp = _make_server()

    def test_filter_basic(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [1, 2, 3, 4, 5], "threshold": 3},
        )
        assert res == {"result": [4, 5]}

    def test_filter_none_pass(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [1, 2, 3], "threshold": 10},
        )
        assert res == {"result": []}

    def test_filter_all_pass(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [10, 20, 30], "threshold": 0},
        )
        assert res == {"result": [10, 20, 30]}

    def test_filter_empty(self):
        res = _call(
            self.mcp, "collection_filter_gt", {"items": [], "threshold": 5}
        )
        assert res == {"result": []}

    def test_filter_equal_not_included(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [3, 3, 3], "threshold": 3},
        )
        assert res == {"result": []}

    def test_filter_floats(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [1.5, 2.5, 3.5], "threshold": 2.0},
        )
        assert res == {"result": [2.5, 3.5]}

    def test_filter_negative_threshold(self):
        res = _call(
            self.mcp,
            "collection_filter_gt",
            {"items": [-5, -1, 0, 1, 5], "threshold": -2},
        )
        assert res == {"result": [-1, 0, 1, 5]}


# ── collection_unique ────────────────────────────────────────────────────────


class TestCollectionUnique:
    def setup_method(self):
        self.mcp = _make_server()

    def test_unique_integers(self):
        res = _call(self.mcp, "collection_unique", {"items": [1, 2, 2, 3, 1]})
        assert res == {"result": [1, 2, 3]}

    def test_unique_strings(self):
        res = _call(
            self.mcp, "collection_unique", {"items": ["a", "b", "a", "c", "b"]}
        )
        assert res == {"result": ["a", "b", "c"]}

    def test_unique_preserves_order(self):
        res = _call(self.mcp, "collection_unique", {"items": [3, 1, 2, 1, 3]})
        assert res == {"result": [3, 1, 2]}

    def test_unique_empty(self):
        res = _call(self.mcp, "collection_unique", {"items": []})
        assert res == {"result": []}

    def test_unique_no_duplicates(self):
        res = _call(self.mcp, "collection_unique", {"items": [1, 2, 3]})
        assert res == {"result": [1, 2, 3]}

    def test_unique_all_same(self):
        res = _call(self.mcp, "collection_unique", {"items": [7, 7, 7]})
        assert res == {"result": [7]}

    def test_unique_mixed_types(self):
        # JSON serialization differentiates 1 (int) from "1" (string)
        res = _call(self.mcp, "collection_unique", {"items": [1, "1", 1, "1"]})
        assert res == {"result": [1, "1"]}

    def test_unique_with_dicts(self):
        res = _call(
            self.mcp,
            "collection_unique",
            {"items": [{"a": 1}, {"b": 2}, {"a": 1}]},
        )
        assert res == {"result": [{"a": 1}, {"b": 2}]}


# ── collection_group_by ──────────────────────────────────────────────────────


class TestCollectionGroupBy:
    def setup_method(self):
        self.mcp = _make_server()

    def test_group_by_basic(self):
        items = [
            {"name": "Alice", "dept": "eng"},
            {"name": "Bob", "dept": "sales"},
            {"name": "Carol", "dept": "eng"},
        ]
        res = _call(
            self.mcp, "collection_group_by", {"items": items, "key": "dept"}
        )
        assert res == {
            "result": {
                "eng": [
                    {"name": "Alice", "dept": "eng"},
                    {"name": "Carol", "dept": "eng"},
                ],
                "sales": [{"name": "Bob", "dept": "sales"}],
            }
        }

    def test_group_by_single_group(self):
        items = [{"x": 1, "g": "a"}, {"x": 2, "g": "a"}]
        res = _call(self.mcp, "collection_group_by", {"items": items, "key": "g"})
        assert len(res["result"]) == 1
        assert len(res["result"]["a"]) == 2

    def test_group_by_missing_key(self):
        items = [{"name": "Alice"}, {"name": "Bob", "dept": "sales"}]
        res = _call(
            self.mcp, "collection_group_by", {"items": items, "key": "dept"}
        )
        assert "error" in res

    def test_group_by_empty_list(self):
        res = _call(
            self.mcp, "collection_group_by", {"items": [], "key": "whatever"}
        )
        assert res == {"result": {}}

    def test_group_by_numeric_key_values(self):
        items = [
            {"val": 1, "group": 10},
            {"val": 2, "group": 20},
            {"val": 3, "group": 10},
        ]
        res = _call(
            self.mcp, "collection_group_by", {"items": items, "key": "group"}
        )
        assert "10" in res["result"]
        assert "20" in res["result"]
        assert len(res["result"]["10"]) == 2


# ── collection_zip ───────────────────────────────────────────────────────────


class TestCollectionZip:
    def setup_method(self):
        self.mcp = _make_server()

    def test_zip_equal_length(self):
        res = _call(
            self.mcp,
            "collection_zip",
            {"list_a": [1, 2, 3], "list_b": ["a", "b", "c"]},
        )
        assert res == {"result": [[1, "a"], [2, "b"], [3, "c"]]}

    def test_zip_unequal_length(self):
        res = _call(
            self.mcp,
            "collection_zip",
            {"list_a": [1, 2], "list_b": ["a", "b", "c"]},
        )
        assert res == {"result": [[1, "a"], [2, "b"]]}

    def test_zip_empty(self):
        res = _call(
            self.mcp, "collection_zip", {"list_a": [], "list_b": []}
        )
        assert res == {"result": []}

    def test_zip_one_empty(self):
        res = _call(
            self.mcp, "collection_zip", {"list_a": [1, 2], "list_b": []}
        )
        assert res == {"result": []}

    def test_zip_single_elements(self):
        res = _call(
            self.mcp, "collection_zip", {"list_a": [1], "list_b": [2]}
        )
        assert res == {"result": [[1, 2]]}


# ── collection_chunk ─────────────────────────────────────────────────────────


class TestCollectionChunk:
    def setup_method(self):
        self.mcp = _make_server()

    def test_chunk_even(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2, 3, 4], "size": 2}
        )
        assert res == {"result": [[1, 2], [3, 4]]}

    def test_chunk_uneven(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2, 3, 4, 5], "size": 2}
        )
        assert res == {"result": [[1, 2], [3, 4], [5]]}

    def test_chunk_size_larger_than_list(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2], "size": 10}
        )
        assert res == {"result": [[1, 2]]}

    def test_chunk_size_one(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2, 3], "size": 1}
        )
        assert res == {"result": [[1], [2], [3]]}

    def test_chunk_empty(self):
        res = _call(self.mcp, "collection_chunk", {"items": [], "size": 3})
        assert res == {"result": []}

    def test_chunk_size_zero_error(self):
        res = _call(self.mcp, "collection_chunk", {"items": [1, 2, 3], "size": 0})
        assert "error" in res

    def test_chunk_negative_size_error(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2, 3], "size": -1}
        )
        assert "error" in res

    def test_chunk_size_equals_length(self):
        res = _call(
            self.mcp, "collection_chunk", {"items": [1, 2, 3], "size": 3}
        )
        assert res == {"result": [[1, 2, 3]]}
