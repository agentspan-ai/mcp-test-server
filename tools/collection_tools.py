"""Collection tools for MCP test server."""

import json


def _flatten(items):
    """Recursively flatten nested lists."""
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(_flatten(item))
        else:
            result.append(item)
    return result


def register(mcp):
    @mcp.tool()
    def collection_sort(items: list, reverse: bool = False) -> str:
        """Sort a list of items.

        Args:
            items: The list to sort.
            reverse: If True, sort in descending order.
        """
        try:
            sorted_items = sorted(items, reverse=reverse)
            return json.dumps({"result": sorted_items})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_flatten(items: list) -> str:
        """Recursively flatten nested lists.

        Args:
            items: A potentially nested list to flatten.
        """
        try:
            result = _flatten(items)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_merge(dict_a: dict, dict_b: dict) -> str:
        """Merge two dictionaries. Values from dict_b win on conflict.

        Args:
            dict_a: The base dictionary.
            dict_b: The dictionary to merge in (wins on conflict).
        """
        try:
            merged = {**dict_a, **dict_b}
            return json.dumps({"result": merged})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_filter_gt(items: list[float], threshold: float) -> str:
        """Filter numbers greater than a threshold.

        Args:
            items: List of numbers to filter.
            threshold: The threshold value.
        """
        try:
            filtered = [x for x in items if x > threshold]
            return json.dumps({"result": filtered})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_unique(items: list) -> str:
        """Remove duplicates from a list, preserving order.

        Uses JSON serialization for dedup keys to handle mixed types.

        Args:
            items: The list to deduplicate.
        """
        try:
            seen = set()
            result = []
            for item in items:
                key = json.dumps(item, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_group_by(items: list[dict], key: str) -> str:
        """Group a list of objects by a key.

        Args:
            items: List of dictionaries to group.
            key: The key to group by.
        """
        try:
            groups = {}
            for item in items:
                group_key = item.get(key)
                if group_key is None:
                    return json.dumps({"error": f"Key '{key}' not found in item: {item}"})
                group_key_str = str(group_key)
                if group_key_str not in groups:
                    groups[group_key_str] = []
                groups[group_key_str].append(item)
            return json.dumps({"result": groups})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_zip(list_a: list, list_b: list) -> str:
        """Zip two lists into a list of pairs.

        Args:
            list_a: The first list.
            list_b: The second list.
        """
        try:
            zipped = [list(pair) for pair in zip(list_a, list_b)]
            return json.dumps({"result": zipped})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def collection_chunk(items: list, size: int) -> str:
        """Split a list into chunks of a given size.

        Args:
            items: The list to split.
            size: The chunk size.
        """
        try:
            if size <= 0:
                return json.dumps({"error": "Chunk size must be positive"})
            chunks = [items[i : i + size] for i in range(0, len(items), size)]
            return json.dumps({"result": chunks})
        except Exception as e:
            return json.dumps({"error": str(e)})
