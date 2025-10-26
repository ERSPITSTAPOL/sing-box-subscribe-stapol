import json
from urllib.parse import parse_qs
def convert(request):
    url = request.args.get("url") or parse_qs(request.query_string).get("url", [None])[0]
    if not url:
        return {
            "status": 400,
            "body": json.dumps({"error": "missing ?url="}),
            "headers": {"content-type": "application/json"}
        }
    result = {"url": url, "message": "success"}
    return {
        "status": 200,
        "body": json.dumps(result),
        "headers": {"content-type": "application/json"}
    }