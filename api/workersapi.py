from flask import Flask, request, jsonify
import main 
app = Flask(__name__)
@app.route("/convert", methods=["GET"])
def convert():
    url = request.args.get("url")
    template = request.args.get("template", "default")
    if not url:
        return jsonify({"error": "missing parameter: url"}), 400
    try:
        if hasattr(main, "convert"):
            result = main.convert(url, template=template)
        elif hasattr(main, "run"):
            result = main.run(url, template=template)
        else:
            return jsonify({"error": "main.py missing convert() or run()"}), 500
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ != "__main__":
    app = app
