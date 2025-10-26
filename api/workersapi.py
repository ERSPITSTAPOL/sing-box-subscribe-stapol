from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route("/")
def index():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing ?url="}), 400
    return jsonify({"url": url, "message": "success"})
def convert(request):
    with app.test_request_context(
        path=request.path,
        base_url=request.base_url,
        query_string=request.query_string
    ):
        resp = app.full_dispatch_request()
        return {
            "status": resp.status_code,
            "body": resp.get_data(as_text=True),
            "headers": dict(resp.headers)
        }