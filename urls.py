from brace.urls.method_urls import *

# --- dummy handlers ---
def home(): return "home"
def get_user(id): return f"user {id}"
def create_user(id): return f"create {id}"
def update_user(id): return f"update {id}"
def delete_user(id): return f"delete {id}"
def post_handler(id, title): return f"{id}-{title}"

# --- setup ---
routes = MethodUrls()

# --- insert endpoints ---
routes.insert_endpoint(HttpMethod.GET, "/", home)
routes.insert_endpoint(HttpMethod.GET, "/user/<int:id>", get_user)
routes.insert_endpoint(HttpMethod.POST, "/user/<int:id>", create_user)
routes.insert_endpoint(HttpMethod.PUT, "/user/<int:id>", update_user)
routes.insert_endpoint(HttpMethod.DELETE, "/user/<int:id>", delete_user)
routes.insert_endpoint(HttpMethod.GET, "/post/<int:id>/<str:title>", post_handler)
routes.insert_endpoint(HttpMethod.GET, "/about", lambda: "about page")

# ----------------------------
# 🔥 TEST RUNNER
# ----------------------------

def test_case(desc, method, path, expect_success):
    res = routes.get_handler(method, path)
    print(f"\n[TEST] {desc}")
    print("Path:", path)
    print("Success:", res.success)
    print("Handler:", res.handler)
    print("Vars:", res.path_vars)

    if res.success != expect_success:
        print("❌ FAILED")
    else:
        print("✅ PASSED")

# ----------------------------
# ✅ BASIC TESTS
# ----------------------------

test_case("Root path", HttpMethod.GET, "/", True)
test_case("Simple param", HttpMethod.GET, "/user/42", True)
test_case("Multiple params", HttpMethod.GET, "/post/10/hello", True)
test_case("Static route", HttpMethod.GET, "/about", True)

# ----------------------------
# ❌ FAILURE CASES
# ----------------------------

test_case("Wrong type (string instead of int)", HttpMethod.GET, "/user/abc", False)
test_case("Missing param", HttpMethod.GET, "/user/", False)
test_case("Extra segment", HttpMethod.GET, "/user/42/extra", False)
test_case("Wrong method", HttpMethod.POST, "/about", False)
test_case("Unknown route", HttpMethod.GET, "/unknown", False)

# ----------------------------
# ⚠️ EDGE CASES
# ----------------------------

test_case("Trailing slash normalize", HttpMethod.GET, "/user/42/", True)
test_case("Multiple slashes normalize", HttpMethod.GET, "//user//42//", True)

# ----------------------------
# 💣 COLLISION TESTS
# ----------------------------

routes.insert_endpoint(HttpMethod.GET, "/user/list", lambda: "user list")

test_case("Literal vs param priority", HttpMethod.GET, "/user/list", True)

# ----------------------------
# 💣 TYPE EDGE CASES
# ----------------------------

test_case("Boolean true", HttpMethod.GET, "/user/true", False)  # depends on your TYPE_REGEX
test_case("Float instead of int", HttpMethod.GET, "/user/3.14", False)

# ----------------------------
# 💣 PARTIAL MATCH (IMPORTANT)
# ----------------------------

test_case("Prefix only (should fail)", HttpMethod.GET, "/user", False)

# ----------------------------
# 💣 MULTIPLE PARAM ROUTES
# ----------------------------

test_case("Wrong order params", HttpMethod.GET, "/post/hello/10", False)

# ----------------------------
# 💣 STRESS INSERT + SEARCH
# ----------------------------

for i in range(100):
    routes.insert_endpoint(HttpMethod.GET, f"/bulk/{i}", lambda: i)

for i in range(100):
    res = routes.get_handler(HttpMethod.GET, f"/bulk/{i}")
    if not res.success:
        print("❌ Bulk test failed at", i)

print("\n🔥 TESTING COMPLETE")