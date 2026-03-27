from brace import Brace
from brace.response import *

app = Brace()

# =========================
# HOME HTML (FRONTEND)
# =========================

@app.get("/")
def home(req):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Brace Dashboard</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                margin: 0;
                padding: 0;
            }

            header {
                background: #1e293b;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                border-bottom: 1px solid #334155;
            }

            .container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                padding: 20px;
            }

            .card {
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }

            h2 {
                margin-top: 0;
                color: #38bdf8;
            }

            input {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 8px;
                border: none;
                outline: none;
            }

            button {
                padding: 10px 15px;
                border: none;
                border-radius: 8px;
                background: #38bdf8;
                color: black;
                cursor: pointer;
                margin-right: 10px;
            }

            button:hover {
                background: #0ea5e9;
            }

            .output {
                background: #020617;
                padding: 10px;
                border-radius: 8px;
                margin-top: 10px;
                height: 200px;
                overflow: auto;
                font-size: 14px;
            }

            .status {
                font-weight: bold;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>

        <header>🚀 Brace Interactive Dashboard</header>

        <div class="container">

            <!-- USER CARD -->
            <div class="card">
                <h2>👤 User Lookup</h2>
                <input id="userId" placeholder="Enter User ID (e.g. 1)">
                <button onclick="getUser()">Fetch</button>
                <div class="output" id="userOutput"></div>
            </div>

            <!-- SEARCH CARD -->
            <div class="card">
                <h2>🔍 Search Engine</h2>
                <input id="query" placeholder="Search users/products">
                <button onclick="search()">Search</button>
                <div class="output" id="searchOutput"></div>
            </div>

            <!-- PRODUCT FILTER -->
            <div class="card">
                <h2>💰 Price Filter</h2>
                <input id="price" placeholder="Enter max price (e.g. 500)">
                <button onclick="filter()">Filter</button>
                <div class="output" id="productOutput"></div>
            </div>

            <!-- SYSTEM STATUS -->
            <div class="card">
                <h2>⚙️ System Status</h2>
                <button onclick="checkActive(true)">Activate</button>
                <button onclick="checkActive(false)">Deactivate</button>
                <div class="status" id="statusOutput"></div>
            </div>

            <!-- API TEST -->
            <div class="card">
                <h2>🧪 API Tester</h2>
                <input id="apiId" placeholder="Enter ID">
                <button onclick="apiTest()">Call API</button>
                <div class="output" id="apiOutput"></div>
            </div>

        </div>

        <script>
            function pretty(data) {
                return JSON.stringify(data, null, 2);
            }

            async function getUser() {
                let id = document.getElementById("userId").value;
                let res = await fetch(`/users/${id}`);
                let out = document.getElementById("userOutput");

                if (!res.ok) {
                    out.innerText = "❌ User not found";
                    return;
                }

                let data = await res.json();
                out.innerText = pretty(data);
            }

            async function search() {
                let q = document.getElementById("query").value;
                let res = await fetch(`/search/${q}`);
                let data = await res.json();
                document.getElementById("searchOutput").innerText = pretty(data);
            }

            async function filter() {
                let price = document.getElementById("price").value;
                let res = await fetch(`/products/${price}/filter`);
                let out = document.getElementById("productOutput");

                if (!res.ok) {
                    out.innerText = "❌ Invalid price";
                    return;
                }

                let data = await res.json();
                out.innerText = pretty(data);
            }

            async function checkActive(flag) {
                let res = await fetch(`/active/${flag}`);
                let text = await res.text();
                document.getElementById("statusOutput").innerText = text;
            }

            async function apiTest() {
                let id = document.getElementById("apiId").value;
                let res = await fetch(`/api/${id}/get`);
                let data = await res.json();
                document.getElementById("apiOutput").innerText = pretty(data);
            }
        </script>

    </body>
    </html>
    """
    return 200, HtmlResponse(html)

# =========================
# BACKEND DATA
# =========================

users = {
    1: {"name": "Alice"},
    2: {"name": "Bob"},
    3: {"name": "Charlie"}
}

products = {
    1: {"name": "Laptop", "price": 999.99},
    2: {"name": "Phone", "price": 499.50},
    3: {"name": "Headphones", "price": 99.99}
}


# =========================
# API ROUTES
# =========================

@app.get("/users/<int:id>")
def get_user(req, id):
    user = users.get(id)
    if not user:
        return 404, PlainTextResponse("User not found")
    return 200, JsonRespone(user)


@app.get("/search/<str:query>")
def search(req, query):
    results = []

    for u in users.values():
        if query.lower() in u["name"].lower():
            results.append(u)

    for p in products.values():
        if query.lower() in p["name"].lower():
            results.append(p)

    return 200, JsonRespone({
        "query": query,
        "results": results
    })


@app.get("/active/<bool:flag>")
def active(req, flag):
    return 200, PlainTextResponse(
        "System ACTIVE" if flag else "System INACTIVE"
    )


# =========================
# EXTRA TEST ROUTES
# =========================

@app.get("/products/<real:price>/filter")
def filter_products(req, price):
    result = {k: v for k, v in products.items() if v["price"] <= price}
    return 200, JsonRespone(result)


@app.get("/api/<int:id>/get")
def api_get(req, id):
    return 200, JsonRespone({"id": id, "msg": "Fetched successfully"})