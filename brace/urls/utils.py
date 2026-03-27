from enum import Enum, auto
import re

class NodeType(Enum):
    STRING = auto()
    INTEGER = auto()
    REAL = auto()
    BOOLEAN = auto()

class MatchType(Enum):
    EXACT = auto()
    REGEX = auto()

VALID_TYPES = {
    'int': NodeType.INTEGER,
    'str': NodeType.STRING,
    'bool': NodeType.BOOLEAN,
    'real': NodeType.REAL
}

TYPE_REGEX = {
    NodeType.BOOLEAN: re.compile(r'^(true|false)$'),
    NodeType.INTEGER: re.compile(r'^-?(0|[1-9][0-9]*)$'),
    NodeType.REAL: re.compile(r'^-?(?:[0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$'),
    NodeType.STRING: re.compile(r'^(?!-?\d+(\.\d+)?([eE][+-]?\d+)?$)[^\s]+$'),
}

class Node:
    def __init__(self, node_type : NodeType, match_type : MatchType, val_or_re : str):
        self.node_type = node_type
        self.match_type = match_type
        self.leaf = True
        self.children = {}
        self.val_or_re = val_or_re
        self.handler = None
    
    def __str__(self):
        return (
            f"Node(type={self.node_type.name}, "
            f"match={self.match_type.name}, "
            f"leaf={self.leaf}, "
            f"value={repr(self.val_or_re)})"
        )

