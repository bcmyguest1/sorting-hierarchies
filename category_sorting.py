import argparse
import json
from collections import deque
from typing import List, Any, Dict


class Node:
    # could be done with attr.s or dataclass instead
    def __init__(self, data: Any = None, children: List = None) -> None:
        if children is None:
            self.children = []
        else:
            self.children = children
        self.data = data
        self.parent = None

    def __str__(self):
        return f"Data: {self.data} - children: {self.children}"


def build_tree_from_list(categories: List[Dict]) -> Node:
    """

    :param categories: list of dicts containing "id" and "parent_id" fields
    :return: root node
    """
    lookup: Dict[int, Node] = {}
    root_node: Node = None

    for category in categories:
        if category["id"] in lookup:
            # if we have seen the node before, it means that this was a parent of a previous node
            # don't create a new node here because it will already have children associated with it
            node = lookup[category["id"]]
            node.data = category
        else:
            # we have never seen this node
            node = Node(category)
            lookup[category["id"]] = node

        if category["parent_id"] is None:
            root_node = node
        else:
            parent_node: Node
            if category["parent_id"] not in lookup:
                # have not seen the parent before
                parent_node = Node()
                lookup[category["parent_id"]] = parent_node
            else:
                # have seen the parent before
                parent_node = lookup[category["parent_id"]]
            # add children to the parent node
            parent_node.children.append(node)
            node.parent = parent_node
    return root_node


def breadth_first_flatten_node_data_to_list(node: Node) -> List:
    """
    Flatten a node to a list
    :param node:
    :return:
    """
    node_data: List = []
    if node is None:
        return node_data

    to_traverse: deque[Node] = deque()
    to_traverse.extend(node.children)
    node_data.append(node.data)
    while len(to_traverse) > 0:
        tmp = to_traverse.pop()
        node_data.append(tmp.data)
        to_traverse.extend(tmp.children)
    return node_data


def sort_categories_for_insert(categories: str) -> str:
    """
    Sorts categories for insertion to DB
    :param categories: json string of format:
        [{"id": 1, "parent_id": null},{"id": 2, "parent_id": 1}]
    :return: json string in insertion order (parents must be inserted before children)
    """
    root_node: Node = build_tree_from_list(json.loads(categories))
    print(root_node)
    categories_in_insertion_order: List[Dict] = breadth_first_flatten_node_data_to_list(root_node)
    return json.dumps(categories_in_insertion_order)


if __name__ == "__main__":
    """
    Simply for testing manually
    """
    parser = argparse.ArgumentParser(description='Pass in json string')
    parser.add_argument('--category_input', type=str,
                        help='a list of json object "categories" with "id" and "parent_id" keys that form a single tree')

    args = parser.parse_args()
    print(args.category_input)
    categories = args.category_input

    print(json.dumps(json.loads(categories), indent=4))

    categories_in_insertion_order: str = sort_categories_for_insert(categories)

    print(json.dumps(json.loads(categories_in_insertion_order), indent=4))
