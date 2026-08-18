#!/usr/bin/env python3

import re
import sys
from collections import OrderedDict


EDGE_RE = re.compile(
    r'^(\s*)([A-Za-z0-9_]+)\s*->\s*([A-Za-z0-9_]+)\s*\[label="([^"]*)"\]\s*;?\s*$'
)


def merge_edges(input_file, output_file):
    # Keep all distinct labels for each source -> destination pair,
    # preserving their first-seen order.
    edges = OrderedDict()
    non_edges = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            match = EDGE_RE.match(line)

            if not match:
                non_edges.append(line)
                continue

            indent, src, dst, label = match.groups()
            key = (src, dst)

            if key not in edges:
                edges[key] = {
                    "indent": indent,
                    "labels": [],
                }

            if label not in edges[key]["labels"]:
                edges[key]["labels"].append(label)

    with open(output_file, "w", encoding="utf-8") as f:
        # Preserve everything that isn't an edge.
        for line in non_edges:
            f.write(line)

        # One edge per source -> destination pair.
        #
        # If exactly one unique label exists, preserve it.
        # If multiple unique labels exist, use "*".
        for (src, dst), data in edges.items():
            labels = data["labels"]
            label = labels[0] if len(labels) == 1 else "*"
            f.write(
                f'{data["indent"]}{src} -> {dst} [label="{label}"];\n'
            )


def main():
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} INPUT.dot OUTPUT.dot",
            file=sys.stderr,
        )
        sys.exit(1)

    merge_edges(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
