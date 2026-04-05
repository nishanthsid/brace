from brace import Brace
from brace.response import JsonResponse, PlainTextResponse, ResponseType
import time
import uuid

app = Brace()

RATE_LIMIT = {}
USER_DB = {
    "token123": {"user": "nishanth", "role": "admin"},
    "token456": {"user": "guest", "role": "user"}
}



@app.pre_request()
def attach_request_id(req):
    req.request_id = str(uuid.uuid4())
    req.start_time = time.time()
    print(f"[PRE] [{req.request_id}] {req.method} {req.path}")
    return req


@app.pre_request()
def rate_limiter(req):
    ip = req.remote_addr or "unknown"
    RATE_LIMIT[ip] = RATE_LIMIT.get(ip, 0) + 1

    if RATE_LIMIT[ip] > 5:
        return JsonResponse({"error": "Too many requests"}, status_code=429)

    return req


@app.pre_request()
def auth_middleware(req):
    token = req.headers.get("Authorization")

    if not token:
        req.user = None
        return req

    user_data = USER_DB.get(token)
    if not user_data:
        return JsonResponse({"error": "Invalid token"}, status_code=401)

    req.user = user_data
    return req


@app.pre_request()
def role_protection(req):
    if req.path.startswith("/admin"):
        if not req.user or req.user.get("role") != "admin":
            return JsonResponse({"error": "Forbidden"}, status_code=403)
    return req


@app.pre_request()
def block_secret(req):
    if req.path == "/secret":
        return PlainTextResponse("Access Denied", status_code=403)
    return req

@app.post_request()
def attach_metadata(data):
    req, resp = data

    if resp.get_resp_type() == ResponseType.JSON:
        payload = resp.get_obj()
        resp = JsonResponse(
            {
                "meta": {
                    "timestamp": time.time(),
                    "request_id": getattr(req, "request_id", None)
                },
                "data": payload
            },
            status_code=resp.get_status_code()
        )

    return req, resp


@app.post_request()
def wrap_response(data):
    req, resp = data

    if resp.get_resp_type() == ResponseType.JSON:
        payload = resp.get_obj()
        resp = JsonResponse(
            {
                "status": "success",
                "payload": payload
            },
            status_code=resp.get_status_code()
        )

    return req, resp


@app.post_request()
def log_response(data):
    req, resp = data

    duration = time.time() - getattr(req, "start_time", time.time())
    print(f"[POST] [{getattr(req, 'request_id', 'NA')}] {req.path} → {resp.get_status_code()} ({duration:.4f}s)")

    return req, resp


@app.post_request()
def error_wrapper(data):
    req, resp = data

    if resp.get_status_code() >= 500:
        resp = JsonResponse(
            {
                "status": "error",
                "message": "Internal Server Error"
            },
            status_code=500
        )

    return req, resp


@app.get("/")
def home(req):
    return PlainTextResponse(f"Hello {getattr(req, 'user', None)}!", status_code=200)


@app.get("/json")
def json_route(req):
    return JsonResponse(
        {
            "message": "This is JSON response",
            "user": getattr(req, "user", None)
        },
        status_code=200
    )


@app.get("/admin/dashboard")
def admin_dashboard(req):
    return JsonResponse(
        {
            "message": "Welcome Admin Dashboard",
            "user": req.user
        },
        status_code=200
    )


@app.get("/slow")
def slow_route(req):
    time.sleep(1)
    return JsonResponse({"message": "Slow response"}, status_code=200)


@app.get("/secret")
def secret(req):
    return PlainTextResponse("You found the secret!", status_code=200)

