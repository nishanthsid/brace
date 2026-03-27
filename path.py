from brace.urls import UrlStorage
from brace.urls import MatchType

s = UrlStorage()

# insert
s.insert("/users")
s.insert("/users/<int:id>")
s.insert("/users/<int:id>/profile")
s.insert("/users/<int:id>/posts")
s.insert("/users/<str:name>/follow")
s.insert("/products")
s.insert("/products/<int:id>")
s.insert("/products/<int:id>/reviews")
s.insert("/products/<real:price>/filter")
s.insert("/active/<bool:flag>")
s.insert("/active/<bool:flag>/details")
s.insert("/search/<str:query>")
s.insert("/api/v1/users")
s.insert("/api/v1/users/<int:id>")
s.insert("/api/v2/products/<int:id>/details")

# print tree
def print_tree(node, indent=0):
    prefix = "  " * indent
    key_label = node.val_or_re if node.match_type == MatchType.EXACT else f"<{node.node_type.name}:{node.val_or_re}>"
    print(f'{prefix}"{key_label}" (leaf={node.leaf})')
    for key, child in node.children.items():
        print_tree(child, indent + 1)

print("=== TREE ===")
print_tree(s.root)

# validate
cases = [
    ("/users",                          True),
    ("/users/42",                       True),
    ("/users/42/profile",               True),
    ("/users/42/posts",                 True),
    ("/users/john/follow",              True),
    ("/users/42/follow",                False),  # 42 is int, not str
    ("/users/john/profile",             False),  # john is str, not int
    ("/products",                       True),
    ("/products/10",                    True),
    ("/products/10/reviews",            True),
    ("/products/9.99/filter",           True),
    ("/products/10/filter",             False),  # 10 is int, not real
    ("/active/true",                    True),
    ("/active/false/details",           True),
    ("/active/yes",                     False),
    ("/search/hello",                   True),
    ("/search/123",                     False),  # 123 is int, not str
    ("/api/v1/users",                   True),
    ("/api/v1/users/99",                True),
    ("/api/v2/products/5/details",      True),
    ("/api/v2/products/five/details",   False),
    ("/nonexistent",                    False),
    ("/users/42/profile/extra",         False),  # too deep
]

print("\n=== VALIDATE ===")
all_passed = True
for path, expected in cases:
    result, pdict = s.search(path)
    status = "PASS" if result == expected else "FAIL"
    if status == "FAIL":
        all_passed = False
    print(f"  [{status}] {path} => {result} (expected {expected}), DICT : {pdict}")

print(f"\n{'All passed!' if all_passed else 'Some tests FAILED.'}")