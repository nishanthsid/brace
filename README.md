# Brace

A minimal WSGI web framework built from scratch on top of Werkzeug. Supports typed URL routing, a composable middleware pipeline, and structured response types.

---

## Features

- **Typed path parameters** — `<int:id>`, `<str:name>`, `<real:price>`, `<bool:flag>` with automatic coercion
- **Fast URL routing** — O(1) dict lookup for plain routes, trie traversal for parameterized routes
- **Pre/post request middleware** — chainable pipeline with short-circuit support
- **Structured responses** — `JsonResponse`, `PlainTextResponse`, `HtmlResponse`, `XmlResponse`
- **HTTP methods** — GET, POST, PUT, DELETE

---

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install werkzeug gunicorn
```

---

## Quickstart

```python
from brace import Brace
from brace.response import JsonResponse, PlainTextResponse

app = Brace()

@app.get("/")
def home(req):
    return PlainTextResponse("Hello, world!", status_code=200)

@app.get("/users/<int:id>")
def get_user(req, id):
    return JsonResponse({"id": id}, status_code=200)
```

Run with Gunicorn:

```bash
gunicorn main:app
```

---

## Routing

Routes are registered with decorators. Plain routes resolve in O(1); parameterized routes use a trie.

```python
@app.get("/posts/<int:id>/<str:slug>")
def get_post(req, id, slug):
    return JsonResponse({"id": id, "slug": slug}, status_code=200)
```

### Supported path parameter types

| Type     | Syntax          | Example segment | Coerced to  |
|----------|-----------------|-----------------|-------------|
| Integer  | `<int:name>`    | `42`            | `int`       |
| String   | `<str:name>`    | `hello`         | `str`       |
| Float    | `<real:name>`   | `3.14`          | `float`     |
| Boolean  | `<bool:name>`   | `true`/`false`  | `bool`      |

Type matching is strict — `/users/<int:id>` will not match `/users/john`.

---

## Middleware

Middleware runs in registration order. Returning a `BaseResponse` from a pre-request middleware short-circuits the chain and skips the route handler.

### Pre-request

Receives the `Request` object. Return the (possibly mutated) request to continue, or a response to abort.

```python
@app.pre_request()
def auth(req):
    if not req.headers.get("Authorization"):
        return JsonResponse({"error": "Unauthorized"}, status_code=401)
    return req
```

### Post-request

Receives a `(request, response)` tuple. Must return the same tuple (optionally modified).

```python
@app.post_request()
def add_header(data):
    req, resp = data
    return req, resp
```

---

## Response types

All response constructors take `(body, status_code)`.

```python
from brace.response import JsonResponse, PlainTextResponse, HtmlResponse, XmlResponse

JsonResponse({"key": "value"}, status_code=200)
PlainTextResponse("OK", status_code=200)
HtmlResponse("<h1>Hello</h1>", status_code=200)
XmlResponse("<root/>", status_code=200)
```

---

## Project structure

```
brace/
  brace.py              # Core WSGI app class
  urls/
    storage.py          # Trie-based URL store
    method_urls.py      # Per-method routing, endpoint validator
    utils.py            # Node types, regex matchers
  middlewares/
    pipeline.py         # Linked-list middleware pipeline
  response/
    types.py            # Response classes and ResponseType enum
  exceptions/
    __init__.py         # InvalidEndpointException
main.py                 # Example app with auth, rate limiting, logging
```

---

## Example app

`main.py` demonstrates a realistic middleware stack:

- **`attach_request_id`** — tags each request with a UUID and start timestamp
- **`rate_limiter`** — sliding 60-second window, max 5 requests per IP (thread-safe)
- **`auth_middleware`** — token-based auth via `Authorization` header
- **`role_protection`** — restricts `/admin/*` to users with `role: admin`
- **`attach_metadata`** — appends timestamp and request ID to JSON responses
- **`wrap_response`** — wraps successful JSON in `{"status": "success", "payload": ...}`
- **`log_response`** — logs method, path, status, and duration
- **`error_wrapper`** — normalises 5xx responses
