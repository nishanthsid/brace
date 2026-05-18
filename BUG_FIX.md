# Bug Fixes

## Bug 1 — `response_sender` crash on non-`BaseResponse` return values

**File:** `brace/brace.py`

**Problem:** The fallback branch for raw (non-`BaseResponse`) handler return values called `method_resp.get_status_code()`, which only exists on `BaseResponse`. Any handler returning a plain string would raise `AttributeError` before the response could be sent.

**Fix:** Replaced `method_resp.get_status_code()` with a hardcoded `200` status and wrapped the value in `str()` for safe serialisation.

---

## Bug 2 — `UrlStorage.insert` clobbered `leaf=True` on shared-prefix routes

**File:** `brace/urls/storage.py`

**Problem:** `insert` unconditionally set `curr.leaf = False` while descending the trie. If `/users` (leaf, handler set) was registered before `/users/<int:id>`, inserting the second route would flip the `users` node to `leaf=False`, corrupting the trie's structural metadata even though the handler pointer was preserved.

**Fix:** Guard the `leaf = False` assignment so it only fires when the current node has no handler (`if curr.handler is None`). A node that is already a registered endpoint stays marked as a leaf regardless of whether it also becomes an internal node later.

---

## Bug 3 — `EndpointValidator` state names were inverted and confusing

**File:** `brace/urls/method_urls.py`

**Problem:** The three states of the `<type:name>` parser were named `LOOK_GT`, `LOOK_COLON`, `LOOK_LT`, where `LOOK_GT` actually triggered on `<` (not `>`), making the code actively misleading to read.

**Fix:** Renamed the states to `LOOK_OPEN`, `LOOK_COLON`, `LOOK_CLOSE` to match what each state is waiting for (`<`, `:`, `>`).

---

## Bug 4 — Rate limiter was not thread-safe and never reset

**File:** `main.py`

**Problem:** The `RATE_LIMIT` dict was mutated by multiple request-handling threads concurrently without a lock, making counter increments a data race. Counts also accumulated forever — once an IP exceeded the limit it was permanently blocked across all future requests.

**Fix:**
- Added `threading.Lock` (`_RATE_LIMIT_LOCK`) around all reads and writes to `RATE_LIMIT`.
- Introduced a 60-second sliding window (`_RATE_LIMIT_WINDOW`). Each IP entry now stores `{"count": n, "start": t}`; the count resets when the window expires.

---

## Bug 5 — Post-middlewares labelled error responses as `"status": "success"`

**File:** `main.py`

**Problem:** `attach_metadata` and `wrap_response` wrapped every JSON response — including 4xx errors from pre-request middleware short-circuits — in a `{"status": "success", ...}` envelope. A `429 Too Many Requests` body would be returned as:

```json
{"status": "success", "payload": {"error": "Too many requests"}}
```

**Fix:** Both middlewares now check `resp.get_status_code() < 400` before wrapping. Error responses pass through untouched with their original body and status code.
