from brace import Brace
from brace.response import *

app = Brace()

# ----------------------------
# BASIC ROUTES
# ----------------------------

@app.get("/")
def home(req):
    return 200, "Hello from Brace"

@app.get("/about")
def about(req):
    return 200, "About page"

# ----------------------------
# PARAM ROUTES
# ----------------------------

@app.get("/user/<int:id>")
def get_user(req, id):
    return 200, JsonRespone({"user_id": id})

@app.post("/user/<int:id>")
def create_user(req, id):
    return 201, JsonRespone({"created": id})

@app.put("/user/<int:id>")
def update_user(req, id):
    return 200, JsonRespone({"updated": id})

@app.delete("/user/<int:id>")
def delete_user(req, id):
    return 200, JsonRespone({"deleted": id})

# ----------------------------
# MULTI PARAM
# ----------------------------

@app.get("/post/<int:id>/<str:title>")
def post(req, id, title):
    return 200, JsonRespone({
        "id": id,
        "title": title
    })

# ----------------------------
# EDGE CASES
# ----------------------------

@app.get("/echo/<str:value>")
def echo(req, value):
    return 200, value

@app.get("/fail")
def fail(req):
    return 500, "forced failure"

# ----------------------------
# PREFIX TEST (should fail)
# ----------------------------

@app.get("/prefix/test")
def prefix(req):
    return 200, "prefix ok"