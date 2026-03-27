from brace.urls.utils import *
from typing import Callable

class UrlStorage:
    def __init__(self):
        self.root = Node(NodeType.STRING, MatchType.EXACT, "$")
    
    @staticmethod
    def normalize_path(path: str):
        path = re.sub(r'/+', '/', path)
        if len(path) > 1 and path.endswith('/'):
            path = path[:-1]
        return path
    
    @staticmethod
    def split_components(url_path: str):
        return [comp for comp in url_path.split("/") if comp]
    
    @staticmethod
    def need_parsing(comp: str):
        if len(comp) < 2 or comp[0] != "<" or comp[-1] != ">":
            return False
        return True
    
    @staticmethod
    def parse_component(comp : str):
        comp = comp[1:-1]
        comp_split = comp.split(":")
        if len(comp_split) != 2:
            raise ValueError(f"Path var syntax not followed {comp}")
        comp_type = comp_split[0].lower()
        var_name = comp_split[1]
        if comp_type not in VALID_TYPES.keys():
            raise TypeError(f"Not a valid type {comp_type}")
        
        node_type = VALID_TYPES[comp_type]

        return Node(node_type, MatchType.REGEX, var_name)
    
    @staticmethod
    def detect_node_type(value: str):
        for node_type in [
            NodeType.BOOLEAN,
            NodeType.INTEGER,
            NodeType.REAL,
            NodeType.STRING,
        ]:
            if TYPE_REGEX[node_type].fullmatch(value):
                return node_type
        return None
    def insert(self, path : str, handler : Callable):
        path = UrlStorage.normalize_path(path)
        split = UrlStorage.split_components(path)
        curr = self.root
        for i in split:
            key = i
            if UrlStorage.need_parsing(i):
                node = UrlStorage.parse_component(i)
                key = node.node_type
            else:
                node = Node(NodeType.STRING, MatchType.EXACT, i)
            
            val = curr.children.get(key, False)
            curr.leaf = False
            if val == False:
                curr.children[key] = node
                curr = node
            else:
                curr = val
        curr.leaf = True
        curr.handler = handler
    
    def search(self, path : str):
        path = UrlStorage.normalize_path(path)
        split = UrlStorage.split_components(path)
        curr = self.root
        path_dict = {}
        res = True
        for i in split:
            node = curr.children.get(i, False)
            if node == False:
                possible = UrlStorage.detect_node_type(i)
                if possible is None:
                    res = False
                    break
                node = curr.children.get(possible, False)
                if node == False:
                    res = False
                    break
                if possible == NodeType.INTEGER:
                    dict_val = int(i)
                elif possible == NodeType.REAL:
                    dict_val = float(i)
                elif possible == NodeType.BOOLEAN:
                    dict_val = True if i.lower() == "true" else False
                else:
                    dict_val = i
                path_dict[node.val_or_re] = dict_val
            curr = node
        handler = None
        if res:
            handler = curr.handler
        return res, path_dict, handler
                